import uuid
from typing import List, Optional, Tuple
from sqlalchemy import or_, func, desc
from sqlalchemy.orm import Session, joinedload
from app.models.resource import Resource
from app.models.category import Category
from app.models.tag import Tag
from app.models.saved_resource import SavedResource
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.services.utils import generate_slug, sanitize_html

def get_unique_slug(db: Session, title: str) -> str:
    base_slug = generate_slug(title)
    if not base_slug:
        base_slug = "resource"
    slug = base_slug
    counter = 1
    while db.query(Resource).filter(Resource.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def create_resource(db: Session, res_in: ResourceCreate, user_id: Optional[int] = None, auto_approve: bool = False) -> Resource:
    slug = get_unique_slug(db, res_in.title)
    cleaned_desc = sanitize_html(res_in.description)
    status = "published" if auto_approve else "pending"

    resource = Resource(
        title=res_in.title.strip(),
        slug=slug,
        description=cleaned_desc,
        category_id=res_in.category_id,
        resource_type=res_in.resource_type.strip(),
        location=res_in.location.strip() if res_in.location else "Remote",
        url=res_in.url.strip(),
        contact=res_in.contact.strip() if res_in.contact else None,
        user_id=user_id,
        status=status
    )

    # Process tags
    if res_in.tags:
        for tag_name in res_in.tags:
            tag_name_clean = tag_name.strip().lower()
            if not tag_name_clean:
                continue
            tag = db.query(Tag).filter(Tag.name == tag_name_clean).first()
            if not tag:
                tag = Tag(name=tag_name_clean)
                db.add(tag)
                db.flush()
            resource.tags.append(tag)

    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

def get_resource_by_slug(db: Session, slug: str) -> Optional[Resource]:
    return db.query(Resource).options(
        joinedload(Resource.category),
        joinedload(Resource.tags),
        joinedload(Resource.submitter)
    ).filter(Resource.slug == slug).first()

def get_resource_by_id(db: Session, resource_id: int) -> Optional[Resource]:
    return db.query(Resource).options(
        joinedload(Resource.category),
        joinedload(Resource.tags)
    ).filter(Resource.id == resource_id).first()

def get_resources(
    db: Session,
    q: Optional[str] = None,
    category_slug: Optional[str] = None,
    resource_type: Optional[str] = None,
    location: Optional[str] = None,
    status: str = "published",
    page: int = 1,
    limit: int = 12
) -> Tuple[List[Resource], int]:
    query = db.query(Resource).options(
        joinedload(Resource.category),
        joinedload(Resource.tags)
    )

    if status:
        query = query.filter(Resource.status == status)

    if category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Resource.category_id == cat.id)

    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)

    if location and location.lower() != "all":
        query = query.filter(Resource.location.ilike(f"%{location}%"))

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Resource.title.ilike(search_term),
                Resource.description.ilike(search_term),
                Resource.location.ilike(search_term),
                Resource.resource_type.ilike(search_term)
            )
        )

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(desc(Resource.created_at)).offset(offset).limit(limit).all()
    
    return items, total

def update_resource(db: Session, resource_id: int, res_update: ResourceUpdate) -> Optional[Resource]:
    res = get_resource_by_id(db, resource_id)
    if not res:
        return None

    update_data = res_update.model_dump(exclude_unset=True)
    if "description" in update_data and update_data["description"]:
        update_data["description"] = sanitize_html(update_data["description"])

    tags_data = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(res, field, value)

    if tags_data is not None:
        res.tags.clear()
        for tag_name in tags_data:
            clean_name = tag_name.strip().lower()
            if clean_name:
                tag = db.query(Tag).filter(Tag.name == clean_name).first()
                if not tag:
                    tag = Tag(name=clean_name)
                    db.add(tag)
                    db.flush()
                res.tags.append(tag)

    db.commit()
    db.refresh(res)
    return res

def toggle_save_resource(db: Session, user_id: int, resource_id: int) -> bool:
    """Toggles saving/bookmarking a resource for a user. Returns True if saved, False if unsaved."""
    existing = db.query(SavedResource).filter(
        SavedResource.user_id == user_id,
        SavedResource.resource_id == resource_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return False
    else:
        saved = SavedResource(user_id=user_id, resource_id=resource_id)
        db.add(saved)
        db.commit()
        return True

def get_user_saved_resources(db: Session, user_id: int) -> List[Resource]:
    saved_items = db.query(SavedResource).filter(SavedResource.user_id == user_id).all()
    resource_ids = [item.resource_id for item in saved_items]
    if not resource_ids:
        return []
    return db.query(Resource).options(joinedload(Resource.category)).filter(Resource.id.in_(resource_ids)).all()

def is_resource_saved_by_user(db: Session, user_id: int, resource_id: int) -> bool:
    count = db.query(SavedResource).filter(
        SavedResource.user_id == user_id,
        SavedResource.resource_id == resource_id
    ).count()
    return count > 0

def get_user_submissions(db: Session, user_id: int) -> List[Resource]:
    return db.query(Resource).options(joinedload(Resource.category)).filter(Resource.user_id == user_id).order_by(desc(Resource.created_at)).all()
