import math
from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.db.session import get_db
from app.services.category_service import get_categories, get_category_by_slug
from app.services.resource_service import (
    get_resources,
    get_resource_by_slug,
    is_resource_saved_by_user
)
from app.web.dependencies import get_current_user_from_cookie
from app.models.user import User

router = APIRouter()

RESOURCE_TYPES = [
    "Opportunity", "Course", "Scholarship", "Job",
    "Internship", "Event", "Community Service", "Tool", "Support", "Other"
]

@router.get("/", response_class=HTMLResponse)
def home_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    categories = get_categories(db)
    recent_resources, total = get_resources(db, status="published", page=1, limit=6)

    return templates.TemplateResponse(
        request=request,
        name="public/home.html",
        context={
            "current_user": current_user,
            "categories": categories,
            "recent_resources": recent_resources,
            "total_count": total,
            "resource_types": RESOURCE_TYPES
        }
    )

@router.get("/resources", response_class=HTMLResponse)
def browse_resources(
    request: Request,
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    categories = get_categories(db)
    limit = 12
    resources, total = get_resources(
        db,
        q=q,
        category_slug=category,
        resource_type=type,
        location=location,
        status="published",
        page=page,
        limit=limit
    )

    total_pages = math.ceil(total / limit) if total > 0 else 1
    selected_cat = get_category_by_slug(db, category) if category else None

    return templates.TemplateResponse(
        request=request,
        name="public/browse.html",
        context={
            "current_user": current_user,
            "resources": resources,
            "categories": categories,
            "resource_types": RESOURCE_TYPES,
            "q": q or "",
            "selected_category": category or "",
            "selected_cat_obj": selected_cat,
            "selected_type": type or "",
            "selected_location": location or "",
            "page": page,
            "total_pages": total_pages,
            "total_items": total
        }
    )

@router.get("/resources/{slug}", response_class=HTMLResponse)
def resource_detail(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    resource = get_resource_by_slug(db, slug)
    if not resource or resource.status != "published":
        if not resource or not (current_user and (current_user.role == "admin" or current_user.id == resource.user_id)):
            raise HTTPException(status_code=404, detail="Resource not found")

    is_saved = False
    if current_user:
        is_saved = is_resource_saved_by_user(db, current_user.id, resource.id)

    related_resources, _ = get_resources(
        db,
        category_slug=resource.category.slug if resource.category else None,
        status="published",
        limit=4
    )
    related = [r for r in related_resources if r.id != resource.id][:3]

    return templates.TemplateResponse(
        request=request,
        name="public/detail.html",
        context={
            "current_user": current_user,
            "resource": resource,
            "is_saved": is_saved,
            "related_resources": related
        }
    )

@router.get("/categories", response_class=HTMLResponse)
def categories_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    categories = get_categories(db)
    return templates.TemplateResponse(
        request=request,
        name="public/categories.html",
        context={
            "current_user": current_user,
            "categories": categories
        }
    )

@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="public/about.html", context={"current_user": current_user})

@router.get("/privacy", response_class=HTMLResponse)
def privacy_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="public/privacy.html", context={"current_user": current_user})

@router.get("/terms", response_class=HTMLResponse)
def terms_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="public/terms.html", context={"current_user": current_user})
