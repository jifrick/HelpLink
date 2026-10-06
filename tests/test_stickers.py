import pytest
from sqlalchemy.orm import Session
from app.models.gamification import Reward, RewardRedemption, UserBadge, Badge
from app.models.user import User
from app.services.points_service import award_points, deduct_points
from app.services.moderation_service import update_resource_status
from app.models.resource import Resource

def setup_test_milestones(db: Session):
    for i in range(1, 11):
        r = Reward(
            name=f"HelpLink Sticker Pack {i:02d}",
            description="Test desc",
            cost_hp=0,
            reward_type="DIGITAL_DOWNLOAD",
            status="READY",
            asset_reference=f"app/static/rewards/test_{i}.zip",
            thumbnail=f"test_{i}.png",
            is_active=True,
            is_milestone=True,
            milestone_threshold=i * 100
        )
        db.add(r)
    db.commit()

def test_milestone_grants(client, db: Session):
    setup_test_milestones(db)
    client.post("/register", data={"full_name": "Test1", "email": "m1@test.com", "password": "Password123!"})
    
    user = db.query(User).filter(User.email == "m1@test.com").first()
    
    # 1. Award 100 points
    award_points(db, user.id, 100, "TEST")
    db.refresh(user)
    
    assert user.helppoints_balance == 100
    assert user.lifetime_helppoints == 100
    
    # Check Pack 01 granted
    pack1 = db.query(Reward).filter(Reward.milestone_threshold == 100).first()
    redemption1 = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=pack1.id).first()
    assert redemption1 is not None
    assert redemption1.status == "FULFILLED"
    
    # Pack 02 not granted
    pack2 = db.query(Reward).filter(Reward.milestone_threshold == 200).first()
    redemption2 = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=pack2.id).first()
    assert redemption2 is None
    
    # 2. Award 150 more points -> Total 250
    award_points(db, user.id, 150, "TEST2")
    db.refresh(user)
    
    assert user.helppoints_balance == 250
    assert user.lifetime_helppoints == 250
    
    redemption2_now = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=pack2.id).first()
    assert redemption2_now is not None
    
    # Point balance deduction does not affect lifetime or ownership
    deduct_points(db, user.id, 200, "REWARD_REDEMPTION", force=True)
    db.refresh(user)
    assert user.helppoints_balance == 50
    assert user.lifetime_helppoints == 250
    
    # Still own packs
    redemption1_still = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=pack1.id).first()
    assert redemption1_still is not None
    
    # 3. Multiple milestones at once
    award_points(db, user.id, 500, "TEST3") # 250 -> 750 (cross 300, 400, 500, 600, 700)
    db.refresh(user)
    assert user.lifetime_helppoints == 750
    
    for th in [300, 400, 500, 600, 700]:
        p = db.query(Reward).filter(Reward.milestone_threshold == th).first()
        r = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=p.id).first()
        assert r is not None, f"Failed to grant milestone {th}"
        
    # 800 not granted
    p800 = db.query(Reward).filter(Reward.milestone_threshold == 800).first()
    r800 = db.query(RewardRedemption).filter_by(user_id=user.id, reward_id=p800.id).first()
    assert r800 is None

def test_level_and_resource_badges(client, db: Session):
    # Setup test category since we rely on it for resources
    from app.models.category import Category
    if not db.query(Category).first():
        cat = Category(name="Test Category", slug="test-category")
        db.add(cat)
        db.commit()
        
    client.post("/register", data={"full_name": "Test2", "email": "m2@test.com", "password": "Password123!"})
    user = db.query(User).filter(User.email == "m2@test.com").first()
    
    assert user.level == "New Contributor"
    
    # 1 resource
    cat_id = db.query(Category).first().id
    res = Resource(user_id=user.id, title="Test", slug="test-res", description="Test", url="http://test.com", category_id=cat_id, resource_type="Opportunity", status="pending")
    db.add(res)
    db.commit()
    
    update_resource_status(db, res.id, "published")
    db.refresh(user)
    
    # Badges
    badges = db.query(Badge).join(UserBadge).filter(UserBadge.user_id == user.id).all()
    badge_names = [b.name for b in badges]
    
    # "Bronze Contributor" should be awarded for 1 approved resource
    assert "Bronze Contributor" in badge_names
    
    # Level should be updated from points (50 points -> still New Contributor)
    assert "New Contributor badge" in badge_names
    
    # Manually award points to level up
    award_points(db, user.id, 500, "TEST")
    db.refresh(user)
    
    badges2 = db.query(Badge).join(UserBadge).filter(UserBadge.user_id == user.id).all()
    badge_names2 = [b.name for b in badges2]
    
    # Next level is Active Contributor (300 points)
    assert "Active Contributor badge" in badge_names2

    # Reject resource
    res_reject = Resource(user_id=user.id, title="Test Reject", slug="test-reject", description="Test", url="http://test.com", category_id=cat_id, resource_type="Opportunity", status="pending")
    db.add(res_reject)
    db.commit()
    
    initial_hp = user.helppoints_balance
    update_resource_status(db, res_reject.id, "rejected")
    db.refresh(user)
    
    # Assert points didn't go up
    assert user.helppoints_balance == initial_hp
    
    # Check that no new badges were granted maliciously (still just Bronze)
    badges_after_reject = db.query(Badge).join(UserBadge).filter(UserBadge.user_id == user.id, Badge.criteria_type == "RESOURCE_COUNT").all()
    assert len(badges_after_reject) == 1
    assert badges_after_reject[0].name == "Bronze Contributor"
