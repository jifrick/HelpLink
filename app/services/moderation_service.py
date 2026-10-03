from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from app.models.resource import Resource
from app.models.report import Report
from app.models.category import Category

def get_pending_resources(db: Session) -> List[Resource]:
    return db.query(Resource).options(
        joinedload(Resource.category),
        joinedload(Resource.submitter)
    ).filter(Resource.status == "pending").order_by(desc(Resource.created_at)).all()

def update_resource_status(db: Session, resource_id: int, status: str) -> Optional[Resource]:
    valid_statuses = {"pending", "published", "rejected", "archived"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}")
        
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        return None
        
    res.status = status
    db.commit()
    db.refresh(res)
    return res

def delete_resource(db: Session, resource_id: int) -> bool:
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        return False
    db.delete(res)
    db.commit()
    return True

def get_admin_dashboard_metrics(db: Session) -> Dict[str, Any]:
    total_resources = db.query(func.count(Resource.id)).scalar() or 0
    pending_submissions = db.query(func.count(Resource.id)).filter(Resource.status == "pending").scalar() or 0
    published_resources = db.query(func.count(Resource.id)).filter(Resource.status == "published").scalar() or 0
    total_reports = db.query(func.count(Report.id)).filter(Report.status == "pending").scalar() or 0
    total_categories = db.query(func.count(Category.id)).scalar() or 0

    return {
        "total_resources": total_resources,
        "pending_submissions": pending_submissions,
        "published_resources": published_resources,
        "total_reports": total_reports,
        "total_categories": total_categories
    }
