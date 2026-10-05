import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resource import Resource
from app.services.points_service import award_points, deduct_points
from app.services.automated_moderation import calculate_risk

def test_point_award_and_level_progression(db: Session):
    # Create test user
    user = User(email="test_points@example.com", full_name="Points Tester", contributor_id="HL-TESTPT")
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.helppoints_balance == 0
    assert user.level == "New Contributor"

    # Award points
    award_points(db, user.id, 50, "RESOURCE_APPROVED", "resource", "1", "Test desc")
    db.refresh(user)
    
    assert user.helppoints_balance == 50
    assert user.level == "New Contributor"

    # Award enough for level up
    award_points(db, user.id, 60, "BONUS", "manual", "2", "Test bonus")
    db.refresh(user)
    
    assert user.helppoints_balance == 110
    assert user.level == "Helpful Contributor"
    
def test_idempotent_points(db: Session):
    user = User(email="test_idem@example.com", full_name="Idem Tester", contributor_id="HL-IDEM")
    db.add(user)
    db.commit()
    
    award_points(db, user.id, 50, "RESOURCE_APPROVED", "resource", "1", "Test desc")
    db.refresh(user)
    assert user.helppoints_balance == 50
    
    # Second time with same reference should not award points
    award_points(db, user.id, 50, "RESOURCE_APPROVED", "resource", "1", "Test desc")
    db.refresh(user)
    assert user.helppoints_balance == 50

def test_point_deduction_insufficient(db: Session):
    user = User(email="test_deduct@example.com", full_name="Deduct Tester", contributor_id="HL-DEDUCT")
    db.add(user)
    db.commit()
    
    # Try to deduct when balance is 0
    success = deduct_points(db, user.id, 50, "REWARD_REDEMPTION")
    assert not success
    db.refresh(user)
    assert user.helppoints_balance == 0

def test_moderation_risk_score(db: Session):
    user = User(email="test_mod@example.com", full_name="Mod Tester", trust_score=50)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    res = Resource(title="Buy Bitcoin Now", description="Make money fast!", url="http://example.com")
    mod_result = calculate_risk(db, res, user)
    
    assert mod_result["risk_score"] > 30
    assert mod_result["decision"] in ["HOLD", "REJECTED"]
    assert "SPAM_KEYWORDS_DETECTED" in mod_result["reason_codes"]
