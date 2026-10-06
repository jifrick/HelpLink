from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.gamification import PointTransaction, UserBadge, Badge

# Configurable Points Rules (could be moved to DB or config)
HP_APPROVED_RESOURCE = 50
HP_QUALITY_BONUS = 15
HP_EXCEPTIONAL_BONUS = 25

# Levels mapping
LEVEL_THRESHOLDS = [
    (3500, "HelpLink Hero"),
    (2000, "Community Champion"),
    (1000, "Trusted Contributor"),
    (600, "Community Builder"),
    (300, "Active Contributor"),
    (100, "Helpful Contributor"),
    (0, "New Contributor"),
]

def get_level_for_points(points: int) -> str:
    for threshold, name in LEVEL_THRESHOLDS:
        if points >= threshold:
            return name
    return "New Contributor"

def get_next_level_info(points: int) -> dict:
    current_idx = 0
    # Thresholds are in descending order
    for i, (threshold, name) in enumerate(LEVEL_THRESHOLDS):
        if points >= threshold:
            current_idx = i
            break
            
    if current_idx == 0:
        # Max level reached
        return {
            "is_max": True,
            "next_level_name": None,
            "points_needed": 0,
            "current_threshold": LEVEL_THRESHOLDS[0][0],
            "next_threshold": LEVEL_THRESHOLDS[0][0],
            "progress_percent": 100
        }
        
    next_threshold, next_level_name = LEVEL_THRESHOLDS[current_idx - 1]
    current_threshold = LEVEL_THRESHOLDS[current_idx][0]
    
    range_total = next_threshold - current_threshold
    points_in_range = points - current_threshold
    percent = int((points_in_range / range_total) * 100) if range_total > 0 else 100
    
    return {
        "is_max": False,
        "next_level_name": next_level_name,
        "points_needed": next_threshold - points,
        "current_threshold": current_threshold,
        "next_threshold": next_threshold,
        "progress_percent": min(100, max(0, percent))
    }

def recalculate_user_level(db: Session, user: User) -> bool:
    new_level = get_level_for_points(user.lifetime_helppoints)
    if user.level != new_level:
        user.level = new_level
        return True
    return False

def award_points(db: Session, user_id: int, amount: int, tx_type: str, ref_type: Optional[str] = None, ref_id: Optional[str] = None, description: Optional[str] = None):
    """Safely award points to a user using the database as authoritative."""
    if amount <= 0:
        return
        
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        return

    # Check for duplicate transactions (idempotent based on reference)
    if ref_type and ref_id:
        existing = db.query(PointTransaction).filter_by(
            user_id=user_id,
            transaction_type=tx_type,
            reference_type=ref_type,
            reference_id=ref_id
        ).first()
        if existing:
            return # Already awarded

    tx = PointTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type=tx_type,
        reference_type=ref_type,
        reference_id=ref_id,
        description=description
    )
    db.add(tx)
    
    user.helppoints_balance += amount
    user.lifetime_helppoints += amount
    
    level_changed = recalculate_user_level(db, user)
    
    from app.services.gamification_service import evaluate_milestones, evaluate_level_badge
    evaluate_milestones(db, user)
    
    if level_changed:
        evaluate_level_badge(db, user)
    
    db.commit()

def deduct_points(db: Session, user_id: int, amount: int, tx_type: str, ref_type: Optional[str] = None, ref_id: Optional[str] = None, description: Optional[str] = None, force: bool = False, auto_commit: bool = True) -> bool:
    """Atomic deduction. Returns False if insufficient funds unless force=True."""
    if amount <= 0:
        return True
        
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        return False

    if not force and user.helppoints_balance < amount:
        return False

    tx = PointTransaction(
        user_id=user_id,
        amount=-amount, # Store as negative
        transaction_type=tx_type,
        reference_type=ref_type,
        reference_id=ref_id,
        description=description
    )
    db.add(tx)
    
    user.helppoints_balance -= amount
    recalculate_user_level(db, user)
    
    if auto_commit:
        db.commit()
    return True
