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
        
    res = update_resource_status(db, resource_id, status_val)
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
