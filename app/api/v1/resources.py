import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.resource import ResourceOut, ResourceListResponse, ResourceCreate
from app.services.resource_service import (
    get_resources,
    get_resource_by_slug,
    create_resource
)
from app.web.dependencies import require_current_user
from app.models.user import User

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("", response_model=ResourceListResponse)
def list_resources_api(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    items, total = get_resources(
        db,
        q=q,
        category_slug=category,
        resource_type=type,
        location=location,
        status="published",
        page=page,
        limit=limit
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/{slug}", response_model=ResourceOut)
def get_resource_api(slug: str, db: Session = Depends(get_db)):
    res = get_resource_by_slug(db, slug)
    if not res or res.status != "published":
        raise HTTPException(status_code=404, detail="Resource not found")
    return res

@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource_api(
    res_in: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    auto_approve = (current_user.role == "admin")
    resource = create_resource(db, res_in, user_id=current_user.id, auto_approve=auto_approve)
    return resource
