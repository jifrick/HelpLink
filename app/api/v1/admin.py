from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.resource import ResourceOut
from app.schemas.report import ReportOut
from app.services.moderation_service import (
    get_pending_resources,
    update_resource_status,
    get_admin_dashboard_metrics
)
from app.services.report_service import get_reports
from app.web.dependencies import require_admin_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/metrics")
def admin_metrics_api(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    return get_admin_dashboard_metrics(db)

@router.get("/pending", response_model=List[ResourceOut])
def admin_pending_api(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    return get_pending_resources(db)

@router.patch("/resources/{resource_id}/status", response_model=ResourceOut)
def admin_status_api(
    resource_id: int,
    status_payload: dict = Body(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    status_val = status_payload.get("status")
    if not status_val:
        raise HTTPException(status_code=400, detail="Missing status field")
    res = update_resource_status(db, resource_id, status_val)
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")
    return res

@router.get("/reports", response_model=List[ReportOut])
def admin_reports_api(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    return get_reports(db)
