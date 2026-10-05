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

def recalculate_user_level(db: Session, user: User) -> bool:
    new_level = get_level_for_points(user.helppoints_balance)
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
    recalculate_user_level(db, user)
    
    db.commit()

def deduct_points(db: Session, user_id: int, amount: int, tx_type: str, ref_type: Optional[str] = None, ref_id: Optional[str] = None, description: Optional[str] = None, force: bool = False) -> bool:
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
    
    db.commit()
    return True
