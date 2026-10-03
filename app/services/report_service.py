from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.report import Report
from app.schemas.report import ReportCreate

def create_report(db: Session, report_in: ReportCreate, user_id: Optional[int] = None) -> Report:
    report = Report(
        resource_id=report_in.resource_id,
        user_id=user_id,
        reason=report_in.reason,
        details=report_in.details,
        status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_reports(db: Session, status: Optional[str] = None) -> List[Report]:
    query = db.query(Report).options(
        joinedload(Report.resource),
        joinedload(Report.user)
    )
    if status:
        query = query.filter(Report.status == status)
    return query.order_by(desc(Report.created_at)).all()

def update_report_status(db: Session, report_id: int, status: str) -> Optional[Report]:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return None
    report.status = status
    db.commit()
    db.refresh(report)
    return report
