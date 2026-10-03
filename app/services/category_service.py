from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.services.utils import generate_slug

def get_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.name.asc()).all()

def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    return db.query(Category).filter(Category.slug == slug).first()

def create_category(db: Session, cat_in: CategoryCreate) -> Category:
    slug = generate_slug(cat_in.name)
    category = Category(
        name=cat_in.name,
        slug=slug,
        description=cat_in.description,
        icon=cat_in.icon or "folder"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
