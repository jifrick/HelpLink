from typing import Optional, List
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.core.templates import templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.resource import ResourceCreate
from app.schemas.report import ReportCreate
from app.core.constants import ALLOWED_RESOURCE_TYPES
from app.services.category_service import get_categories, get_category_by_id
from app.services.resource_service import (
    create_resource,
    get_user_submissions,
    get_user_saved_resources,
    toggle_save_resource,
    get_resource_by_id
)
from app.services.report_service import create_report
from app.services.utils import validate_url_string
from app.web.dependencies import require_current_user, get_current_user_from_cookie, validate_csrf_and_origin
from app.models.user import User

router = APIRouter()

RESOURCE_TYPES = ALLOWED_RESOURCE_TYPES

@router.get("/submit", response_class=HTMLResponse)
def submit_resource_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    categories = get_categories(db)
    return templates.TemplateResponse(
        request=request,
        name="user/submit.html",
        context={
            "current_user": current_user,
            "categories": categories,
            "resource_types": RESOURCE_TYPES,
            "error": None
        }
    )

@router.post("/submit", response_class=HTMLResponse)
def submit_resource_process(
    request: Request,
    title: str = Form(...),
    category_id: int = Form(...),
    resource_type: str = Form(...),
    location: str = Form(...),
    url: str = Form(...),
    description: str = Form(...),
    contact: Optional[str] = Form(None),
    tags_raw: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
    _: None = Depends(validate_csrf_and_origin)
):
    categories = get_categories(db)
    form_data = {
        "title": title,
        "category_id": category_id,
        "resource_type": resource_type,
        "location": location,
        "url": url,
        "description": description,
        "contact": contact,
        "tags_raw": tags_raw
    }

    # 1. Validate Category Exists
    category = get_category_by_id(db, category_id)
    if not category:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "The selected category does not exist.",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # 2. Validate Resource Type
    if resource_type.strip() not in RESOURCE_TYPES:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "The selected resource type is invalid.",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # 3. Validate Title & Description
    if len(title.strip()) < 5:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "Title must contain at least 5 characters.",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if len(description.strip()) < 20:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "Description must contain at least 20 characters.",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # 4. Robust URL Validation
    clean_url = url.strip()
    if not validate_url_string(clean_url):
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "Please enter a valid URL starting with http:// or https://",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    auto_approve = (current_user.role == "admin")

    try:
        res_in = ResourceCreate(
            title=title.strip(),
            description=description.strip(),
            category_id=category_id,
            resource_type=resource_type.strip(),
            location=location.strip() if location else "Remote",
            url=clean_url,
            contact=contact.strip() if contact else None,
            tags=tags
        )
        resource = create_resource(db, res_in, user_id=current_user.id, auto_approve=auto_approve)
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": f"Failed to submit resource: {str(exc)}",
                "form": form_data
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return RedirectResponse(
        url=f"/dashboard?submitted=true&status={resource.status}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/dashboard", response_class=HTMLResponse)
def user_dashboard(
    request: Request,
    submitted: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    submissions = get_user_submissions(db, current_user.id)
    saved_items = get_user_saved_resources(db, current_user.id)

    return templates.TemplateResponse(
        request=request,
        name="user/dashboard.html",
        context={
            "current_user": current_user,
            "submissions": submissions,
            "saved_items": saved_items,
            "submitted": submitted,
            "submitted_status": status
        }
    )

@router.get("/saved", response_class=HTMLResponse)
def saved_resources_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    saved_items = get_user_saved_resources(db, current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="user/saved.html",
        context={
            "current_user": current_user,
            "saved_items": saved_items
        }
    )

@router.post("/resources/{resource_id}/toggle-save")
def toggle_save(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
    _: None = Depends(validate_csrf_and_origin)
):
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    is_saved = toggle_save_resource(db, current_user.id, resource_id)
    return JSONResponse(content={"saved": is_saved, "resource_id": resource_id})

@router.post("/resources/{resource_id}/report")
def submit_resource_report(
    resource_id: int,
    reason: str = Form(...),
    details: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie),
    _: None = Depends(validate_csrf_and_origin)
):
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        report_in = ReportCreate(resource_id=resource_id, reason=reason, details=details)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_id = current_user.id if current_user else None
    create_report(db, report_in, user_id=user_id)

    return RedirectResponse(
        url=f"/resources/{resource.slug}?reported=true",
        status_code=status.HTTP_303_SEE_OTHER
    )
