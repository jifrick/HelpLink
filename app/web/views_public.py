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
        name="pages/home.html",
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
        name="pages/browse.html",
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
        name="pages/detail.html",
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
        name="pages/categories.html",
        context={
            "current_user": current_user,
            "categories": categories
        }
    )

@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="pages/about.html", context={"current_user": current_user})

@router.get("/privacy", response_class=HTMLResponse)
def privacy_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="pages/privacy.html", context={"current_user": current_user})

@router.get("/profile/{contributor_id}", response_class=HTMLResponse)
def public_profile(
    contributor_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    from sqlalchemy.orm import joinedload
    from app.models.gamification import UserBadge, Badge
    from app.models.resource import Resource
    
    target_user = db.query(User).filter(User.contributor_id == contributor_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Contributor not found")
        
    user_badges = db.query(UserBadge).options(joinedload(UserBadge.badge)).filter(UserBadge.user_id == target_user.id).order_by(UserBadge.awarded_at.desc()).all()
    owned_badge_ids = [ub.badge_id for ub in user_badges]
    
    # Get all contribution badges ordered by threshold
    all_contribution_badges = db.query(Badge).filter(Badge.criteria_type == "RESOURCE_COUNT").order_by(Badge.threshold.asc()).all()
    
    public_contributions = db.query(Resource).filter(Resource.user_id == target_user.id, Resource.status == "published").order_by(Resource.created_at.desc()).limit(10).all()
    contribution_count = db.query(Resource).filter(Resource.user_id == target_user.id, Resource.status == "published").count()

    next_badge = None
    for b in all_contribution_badges:
        if contribution_count < b.threshold:
            next_badge = b
            break

    return templates.TemplateResponse(
        request=request,
        name="pages/profile.html",
        context={
            "current_user": current_user,
            "profile_user": target_user,
            "user_badges": user_badges,
            "owned_badge_ids": owned_badge_ids,
            "all_contribution_badges": all_contribution_badges,
            "public_contributions": public_contributions,
            "contribution_count": contribution_count,
            "next_badge": next_badge
        }
    )

@router.get("/terms", response_class=HTMLResponse)
def terms_page(request: Request, current_user: Optional[User] = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="pages/terms.html", context={"current_user": current_user})
