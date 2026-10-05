from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.templates import templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.category import CategoryCreate
from app.core.constants import ALLOWED_RESOURCE_STATUSES, ALLOWED_REPORT_STATUSES
from app.services.moderation_service import (
    get_admin_dashboard_metrics,
    get_pending_resources,
    update_resource_status,
    delete_resource
)
from app.services.report_service import get_reports, update_report_status
from app.services.category_service import get_categories, create_category
from app.web.dependencies import require_admin_user, validate_csrf_and_origin
from app.models.user import User

router = APIRouter(prefix="/admin")

@router.get("", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    metrics = get_admin_dashboard_metrics(db)
    pending_items = get_pending_resources(db)
    recent_reports = get_reports(db, status="pending")

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "current_user": admin_user,
            "metrics": metrics,
            "pending_items": pending_items,
            "recent_reports": recent_reports
        }
    )

@router.get("/moderation", response_class=HTMLResponse)
def admin_moderation_queue(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    pending_items = get_pending_resources(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/moderation.html",
        context={
            "current_user": admin_user,
            "pending_items": pending_items
        }
    )

@router.get("/fraud-events", response_class=HTMLResponse)
def admin_fraud_events(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    from app.models.gamification import FraudEvent
    from sqlalchemy.orm import joinedload
    events = db.query(FraudEvent).options(
        joinedload(FraudEvent.user),
        joinedload(FraudEvent.resource)
    ).order_by(FraudEvent.created_at.desc()).limit(100).all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/fraud_events.html",
        context={
            "current_user": admin_user,
            "events": events
        }
    )

@router.post("/resources/{resource_id}/status")
def admin_update_status(
    resource_id: int,
    status_val: str = Form(..., alias="status"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user),
    _: None = Depends(validate_csrf_and_origin)
):
    if status_val not in ALLOWED_RESOURCE_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid resource status provided. Allowed: {', '.join(ALLOWED_RESOURCE_STATUSES)}")
        
    res = update_resource_status(db, resource_id, status_val, admin_user.id)
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")
    return RedirectResponse(url="/admin/dashboard?updated=true", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/resources/{resource_id}/delete")
def admin_delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user),
    _: None = Depends(validate_csrf_and_origin)
):
    success = delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return RedirectResponse(url="/admin/dashboard?deleted=true", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/reports", response_class=HTMLResponse)
def admin_reports(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    reports = get_reports(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/reports.html",
        context={
            "current_user": admin_user,
            "reports": reports
        }
    )

@router.post("/reports/{report_id}/status")
def admin_update_report(
    report_id: int,
    status_val: str = Form(..., alias="status"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user),
    _: None = Depends(validate_csrf_and_origin)
):
    if status_val not in ALLOWED_REPORT_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid report status provided. Allowed: {', '.join(ALLOWED_REPORT_STATUSES)}")

    rep = update_report_status(db, report_id, status_val)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return RedirectResponse(url="/admin/reports?updated=true", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/categories", response_class=HTMLResponse)
def admin_categories(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    categories = get_categories(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/categories.html",
        context={
            "current_user": admin_user,
            "categories": categories,
            "error": None
        }
    )

@router.post("/categories", response_class=HTMLResponse)
def admin_create_category(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    icon: Optional[str] = Form("folder"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user),
    _: None = Depends(validate_csrf_and_origin)
):
    categories = get_categories(db)
    if not name.strip():
        return templates.TemplateResponse(
            request=request,
            name="admin/categories.html",
            context={
                "current_user": admin_user,
                "categories": categories,
                "error": "Category name cannot be empty."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    cat_in = CategoryCreate(name=name.strip(), description=description, icon=icon)
    create_category(db, cat_in)

    return RedirectResponse(url="/admin/categories?created=true", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/contributors", response_class=HTMLResponse)
def admin_contributors(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    users = db.query(User).order_by(User.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/contributors.html",
        context={"current_user": admin_user, "users": users}
    )

@router.get("/contributors/{user_id}", response_class=HTMLResponse)
def admin_contributor_detail(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    from sqlalchemy.orm import joinedload
    from app.models.gamification import PointTransaction, FraudEvent, RewardRedemption, UserBadge
    from app.models.resource import Resource
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    transactions = db.query(PointTransaction).filter(PointTransaction.user_id == target_user.id).order_by(PointTransaction.created_at.desc()).limit(20).all()
    fraud_events = db.query(FraudEvent).filter(FraudEvent.user_id == target_user.id).order_by(FraudEvent.created_at.desc()).all()
    resources = db.query(Resource).filter(Resource.user_id == target_user.id).order_by(Resource.created_at.desc()).limit(10).all()
    redemptions = db.query(RewardRedemption).options(joinedload(RewardRedemption.reward)).filter(RewardRedemption.user_id == target_user.id).order_by(RewardRedemption.created_at.desc()).all()
    badges = db.query(UserBadge).options(joinedload(UserBadge.badge)).filter(UserBadge.user_id == target_user.id).order_by(UserBadge.awarded_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/contributor_detail.html",
        context={
            "current_user": admin_user,
            "target_user": target_user,
            "transactions": transactions,
            "fraud_events": fraud_events,
            "resources": resources,
            "redemptions": redemptions,
            "badges": badges
        }
    )

@router.post("/contributors/{user_id}/points")
def admin_adjust_points(
    user_id: int,
    amount: int = Form(...),
    reason: str = Form(...),
    action_type: str = Form(...),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user),
    _: None = Depends(validate_csrf_and_origin)
):
    from app.services.points_service import award_points, deduct_points
    from app.services.moderation_service import log_admin_action
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if action_type == "add":
        award_points(db, user_id, amount, "ADMIN_ADJUSTMENT", description=f"Admin: {reason}")
        log_admin_action(db, admin_user.id, "AWARD_POINTS", f"User {user_id}", f"Awarded {amount} HP: {reason}")
    elif action_type == "deduct":
        deduct_points(db, user_id, amount, "ADMIN_ADJUSTMENT", description=f"Admin: {reason}", force=True)
        log_admin_action(db, admin_user.id, "DEDUCT_POINTS", f"User {user_id}", f"Deducted {amount} HP: {reason}")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    return RedirectResponse(url=f"/admin/contributors/{user_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/rewards", response_class=HTMLResponse)
def admin_rewards_view(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    from app.models.gamification import Reward, RewardRedemption
    from sqlalchemy.orm import joinedload
    
    rewards = db.query(Reward).order_by(Reward.cost_hp).all()
    redemptions = db.query(RewardRedemption).options(joinedload(RewardRedemption.reward), joinedload(RewardRedemption.user)).order_by(RewardRedemption.created_at.desc()).limit(50).all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/rewards.html",
        context={"current_user": admin_user, "rewards": rewards, "redemptions": redemptions}
    )

@router.get("/audit-logs", response_class=HTMLResponse)
def admin_audit_logs(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_user)
):
    from app.models.gamification import AdminAuditLog
    from sqlalchemy.orm import joinedload
    
    logs = db.query(AdminAuditLog).options(joinedload(AdminAuditLog.admin)).order_by(AdminAuditLog.created_at.desc()).limit(200).all()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/audit_logs.html",
        context={"current_user": admin_user, "logs": logs}
    )
