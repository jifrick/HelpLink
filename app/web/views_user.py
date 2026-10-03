from typing import Optional, List
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.resource import ResourceCreate
from app.schemas.report import ReportCreate
from app.services.category_service import get_categories
from app.services.resource_service import (
    create_resource,
    get_user_submissions,
    get_user_saved_resources,
    toggle_save_resource,
    get_resource_by_id
)
from app.services.report_service import create_report
from app.web.dependencies import require_current_user, get_current_user_from_cookie
from app.models.user import User

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

RESOURCE_TYPES = [
    "Opportunity", "Course", "Scholarship", "Job",
    "Internship", "Event", "Community Service", "Tool", "Support", "Other"
]

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
    current_user: User = Depends(require_current_user)
):
    categories = get_categories(db)

    if len(title.strip()) < 5:
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "Title must contain at least 5 characters.",
                "form": {"title": title, "category_id": category_id, "resource_type": resource_type, "location": location, "url": url, "description": description, "contact": contact, "tags_raw": tags_raw}
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
                "form": {"title": title, "category_id": category_id, "resource_type": resource_type, "location": location, "url": url, "description": description, "contact": contact, "tags_raw": tags_raw}
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not url.strip().startswith(("http://", "https://")):
        return templates.TemplateResponse(
            request=request,
            name="user/submit.html",
            context={
                "current_user": current_user,
                "categories": categories,
                "resource_types": RESOURCE_TYPES,
                "error": "Please enter a valid URL starting with http:// or https://",
                "form": {"title": title, "category_id": category_id, "resource_type": resource_type, "location": location, "url": url, "description": description, "contact": contact, "tags_raw": tags_raw}
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

    auto_approve = (current_user.role == "admin")

    res_in = ResourceCreate(
        title=title,
        description=description,
        category_id=category_id,
        resource_type=resource_type,
        location=location,
        url=url,
        contact=contact,
        tags=tags
    )

    resource = create_resource(db, res_in, user_id=current_user.id, auto_approve=auto_approve)

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
    current_user: User = Depends(require_current_user)
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
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    report_in = ReportCreate(resource_id=resource_id, reason=reason, details=details)
    user_id = current_user.id if current_user else None
    create_report(db, report_in, user_id=user_id)

    return RedirectResponse(
        url=f"/resources/{resource.slug}?reported=true",
        status_code=status.HTTP_303_SEE_OTHER
    )
