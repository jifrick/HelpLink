import uuid
import os
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.templates import templates
from app.db.session import get_db
from app.models.gamification import Reward, RewardRedemption
from app.models.user import User
from app.web.dependencies import require_current_user, validate_csrf_and_origin
from app.services.points_service import deduct_points

router = APIRouter()

@router.get("/rewards", response_class=HTMLResponse)
def rewards_store(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    # Fetch active and visible rewards
    rewards = db.query(Reward).filter(Reward.status.in_(["READY", "COMING_SOON", "UNAVAILABLE"]), Reward.is_active == True).order_by(Reward.cost_hp).all()
    # Fetch user redemptions
    redemptions = db.query(RewardRedemption).filter(RewardRedemption.user_id == current_user.id).order_by(RewardRedemption.created_at.desc()).all()
    
    owned_reward_ids = [r.reward_id for r in redemptions]

    return templates.TemplateResponse(
        request=request,
        name="user/rewards.html",
        context={
            "current_user": current_user,
            "rewards": rewards,
            "redemptions": redemptions,
            "owned_reward_ids": owned_reward_ids
        }
    )

@router.post("/rewards/{reward_id}/redeem")
def redeem_reward(
    reward_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    reward = db.query(Reward).filter(Reward.id == reward_id, Reward.status == "READY", Reward.is_active == True).first()
    if not reward:
        return JSONResponse(status_code=400, content={"error": "Reward is not currently available for redemption."})
        
    # Check if already owned
    existing_redemption = db.query(RewardRedemption).filter(RewardRedemption.user_id == current_user.id, RewardRedemption.reward_id == reward.id).first()
    if existing_redemption:
        return JSONResponse(status_code=400, content={"error": "You already own this reward."})
        
    try:
        # Atomic point deduction (no auto commit)
        success = deduct_points(
            db=db,
            user_id=current_user.id,
            amount=reward.cost_hp,
            tx_type="REWARD_REDEMPTION",
            ref_type="reward",
            ref_id=str(reward.id),
            description=f"Redeemed reward: {reward.name}",
            auto_commit=False
        )
        
        if not success:
            db.rollback()
            return JSONResponse(status_code=400, content={"error": "Insufficient HelpPoints."})
            
        # Create redemption record
        redemption_id = f"RWD-{uuid.uuid4().hex[:8].upper()}"
        redemption = RewardRedemption(
            user_id=current_user.id,
            reward_id=reward.id,
            status="FULFILLED" if reward.reward_type == "DIGITAL_DOWNLOAD" else "PENDING",
            redemption_id=redemption_id
        )
        db.add(redemption)
        db.commit()
        
        return JSONResponse(status_code=200, content={"success": True, "message": "Reward redeemed successfully!", "status": redemption.status, "redemption_id": redemption.redemption_id})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "An error occurred during fulfillment. Your points have not been deducted."})


@router.get("/rewards/{reward_id}/download")
def download_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    # Verify ownership
    redemption = db.query(RewardRedemption).filter(RewardRedemption.user_id == current_user.id, RewardRedemption.reward_id == reward_id, RewardRedemption.status == "FULFILLED").first()
    if not redemption:
        raise HTTPException(status_code=403, detail="You do not own this reward or it is not fulfilled.")
        
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward or not reward.asset_reference:
        raise HTTPException(status_code=404, detail="Reward asset not found.")
        
    file_path = os.path.join(os.getcwd(), reward.asset_reference)
    
    # Path traversal protection
    if not os.path.abspath(file_path).startswith(os.getcwd()):
        raise HTTPException(status_code=400, detail="Invalid path")
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="The reward file is currently unavailable.")
        
    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
