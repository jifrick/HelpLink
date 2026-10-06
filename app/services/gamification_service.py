from sqlalchemy.orm import Session
from app.models.user import User
from app.models.gamification import Reward, RewardRedemption, Badge, UserBadge
import uuid

def evaluate_milestones(db: Session, user: User):
    """
    Evaluates lifetime_helppoints and grants any eligible milestone rewards.
    Assumes caller will db.commit() if auto_commit is False, but we auto_commit here for safety.
    """
    if user.lifetime_helppoints <= 0:
        return
        
    # Get all active milestone rewards
    milestones = db.query(Reward).filter(
        Reward.is_milestone == True,
        Reward.is_active == True,
        Reward.status == "READY"
    ).all()
    
    for milestone in milestones:
        if milestone.milestone_threshold is not None and user.lifetime_helppoints >= milestone.milestone_threshold:
            # Check if user already has it
            existing = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=milestone.id).first()
            if not existing:
                redemption = RewardRedemption(
                    user_id=user.id,
                    reward_id=milestone.id,
                    status="FULFILLED",
                    redemption_id=str(uuid.uuid4())
                )
                db.add(redemption)
                db.flush()

def evaluate_level_badge(db: Session, user: User):
    """
    Grants a badge corresponding to the user's level if one exists.
    """
    if not user.level:
        return
        
    badge_name = f"{user.level} badge"
    
    badge = db.query(Badge).filter(Badge.name == badge_name).first()
    if not badge:
        # Auto-create level badges if they don't exist
        badge = Badge(
            name=badge_name,
            description=f"Awarded for reaching the {user.level} level.",
            icon="award",
            criteria_type="LEVEL",
            threshold=0
        )
        db.add(badge)
        db.flush()
        
    existing = db.query(UserBadge).filter_by(user_id=user.id, badge_id=badge.id).first()
    if not existing:
        ub = UserBadge(user_id=user.id, badge_id=badge.id)
        db.add(ub)
        db.flush()

def evaluate_resource_badges(db: Session, user: User, approved_count: int):
    """
    Grants badges based on approved resource count.
    """
    RESOURCE_MILESTONES = [
        (1, "Bronze Contributor", "Shared your first approved resource"),
        (5, "Helpful Contributor", "Shared 5 approved resources"),
        (10, "Silver Contributor", "Shared 10 approved resources"),
        (25, "Community Builder", "Shared 25 approved resources"),
        (50, "Gold Contributor", "Shared 50 approved resources"),
        (100, "Community Champion", "Shared 100 approved resources"),
        (250, "HelpLink Legend", "Shared 250 approved resources")
    ]
    
    for threshold, name, desc in RESOURCE_MILESTONES:
        if approved_count >= threshold:
            badge = db.query(Badge).filter(Badge.name == name).first()
            if not badge:
                badge = Badge(
                    name=name,
                    description=desc,
                    icon="file-text",
                    criteria_type="RESOURCE_COUNT",
                    threshold=threshold
                )
                db.add(badge)
                db.flush()
                
            existing = db.query(UserBadge).filter_by(user_id=user.id, badge_id=badge.id).first()
            if not existing:
                ub = UserBadge(user_id=user.id, badge_id=badge.id)
                db.add(ub)
                db.flush()
