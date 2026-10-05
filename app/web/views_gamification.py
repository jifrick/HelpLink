import uuid
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
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
    redeemed: Optional[bool] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    # Fetch active rewards
    rewards = db.query(Reward).filter(Reward.is_active == True).order_by(Reward.cost_hp).all()
    # Fetch user redemptions
    redemptions = db.query(RewardRedemption).filter(RewardRedemption.user_id == current_user.id).order_by(RewardRedemption.created_at.desc()).all()
    
    return templates.TemplateResponse(
        request=request,
        name="user/rewards.html",
        context={
            "current_user": current_user,
            "rewards": rewards,
            "redemptions": redemptions,
            "redeemed": redeemed,
            "error": error
        }
    )

@router.post("/rewards/{reward_id}/redeem")
def redeem_reward(
    reward_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
    _: None = Depends(validate_csrf_and_origin)
):
    reward = db.query(Reward).filter(Reward.id == reward_id, Reward.is_active == True).first()
    if not reward:
        return RedirectResponse(url="/rewards?error=Reward not found or inactive", status_code=status.HTTP_303_SEE_OTHER)
        
    # Atomic point deduction
    success = deduct_points(
        db=db,
        user_id=current_user.id,
        amount=reward.cost_hp,
        tx_type="REWARD_REDEMPTION",
        ref_type="reward",
        ref_id=str(reward.id), # Not quite right if they redeem multiple times, but ok for now
        description=f"Redeemed reward: {reward.name}"
    )
    
    if not success:
        return RedirectResponse(url="/rewards?error=Insufficient HelpPoints", status_code=status.HTTP_303_SEE_OTHER)
        
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
    
    return RedirectResponse(url="/rewards?redeemed=true", status_code=status.HTTP_303_SEE_OTHER)
