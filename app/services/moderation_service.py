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

def update_resource_status(db: Session, resource_id: int, status: str, admin_user_id: Optional[int] = None) -> Optional[Resource]:
    valid_statuses = {"pending", "published", "rejected", "archived"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}")
        
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        return None
        
    old_status = res.status
    res.status = status
    
    if admin_user_id:
        from app.models.gamification import AdminAuditLog
        audit = AdminAuditLog(
            admin_id=admin_user_id,
            action="UPDATE_RESOURCE_STATUS",
            target_type="resource",
            target_id=str(res.id),
            reason=f"Status changed from {old_status} to {status}"
        )
        db.add(audit)
    
    if old_status != "published" and status == "published":
        from app.services.points_service import award_points, HP_APPROVED_RESOURCE
        from app.models.gamification import AdminAuditLog
        award_points(db, res.user_id, HP_APPROVED_RESOURCE, "RESOURCE_APPROVED", "resource", str(res.id), f"Resource published: {res.title}")
        
    elif old_status == "published" and status != "published":
        from app.services.points_service import deduct_points, HP_APPROVED_RESOURCE
        from app.models.gamification import AdminAuditLog
        deduct_points(db, res.user_id, HP_APPROVED_RESOURCE, "RESOURCE_REVERSED", "resource", str(res.id), f"Resource unpublished: {res.title}", force=True)

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
