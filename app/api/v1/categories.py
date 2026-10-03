from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.category import CategoryOut
from app.services.category_service import get_categories

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=List[CategoryOut])
def list_categories_api(db: Session = Depends(get_db)):
    return get_categories(db)
