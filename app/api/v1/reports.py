from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.report import ReportCreate, ReportOut
from app.services.report_service import create_report
from app.web.dependencies import get_current_user_from_cookie
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report_api(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    user_id = current_user.id if current_user else None
    return create_report(db, report_in, user_id=user_id)
