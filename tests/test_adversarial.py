import pytest
from sqlalchemy.orm import Session
from app.models.gamification import FraudEvent, AdminAuditLog, PointTransaction
from app.models.user import User
from app.models.resource import Resource

def test_duplicate_url_abuse(client, db: Session):
    client.post("/register", data={"full_name": "Adv1", "email": "adv1@test.com", "password": "Password123!"})
    
    # First submission
    res1 = client.post("/submit", data={
        "title": "Good Resource",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://example.org/unique",
        "description": "This is a valid test resource description with enough length."
    }, follow_redirects=False)
    assert res1.status_code == 303
    
    # Second submission with tracking params
    res2 = client.post("/submit", data={
        "title": "Another Good Resource",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://example.org/unique?utm_source=spam",
        "description": "This is a valid test resource description with enough length."
    }, follow_redirects=False)
    assert res2.status_code == 303
    
    # The first should be published (low risk), the second should be rejected or pending (high risk)
    r1 = db.query(Resource).filter(Resource.title == "Good Resource").first()
    r2 = db.query(Resource).filter(Resource.title == "Another Good Resource").first()
    
    assert r1.status == "published"
    assert r2.status in ["rejected", "pending"]
    assert "DUPLICATE_URL" in r2.fraud_events[0].reason if r2.status == "rejected" else True

def test_spam_burst(client, db: Session):
    client.post("/register", data={"full_name": "Adv2", "email": "adv2@test.com", "password": "Password123!"})
    
    for i in range(6):
        client.post("/submit", data={
            "title": f"Burst Resource {i}",
            "category_id": 1,
            "resource_type": "Course",
            "location": "Remote",
            "url": f"https://example.org/burst{i}",
            "description": "This is a valid test resource description with enough length."
        }, follow_redirects=False)
        
    last_res = db.query(Resource).filter(Resource.title == "Burst Resource 5").first()
    assert last_res.status == "rejected"
    assert last_res.risk_score >= 100

def test_banned_user_blocked(client, db: Session):
    client.post("/register", data={"full_name": "Adv3", "email": "adv3@test.com", "password": "Password123!"})
    
    # Ban the user
    u = db.query(User).filter(User.email == "adv3@test.com").first()
    u.account_status = "BANNED"
    db.commit()
    
    # Try to submit
    res = client.post("/submit", data={
        "title": "I am banned",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://example.org/banned",
        "description": "This is a valid test resource description with enough length."
    }, follow_redirects=False)
    
    # Should get 403 Forbidden
    assert res.status_code == 403

def test_point_reversal_and_audit(client, db: Session):
    client.post("/register", data={"full_name": "Adv4", "email": "adv4@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "adv4@test.com", "password": "Password123!"})
    
    client.post("/submit", data={
        "title": "Valid Resource For Points",
        "category_id": 1,
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://example.org/points",
        "description": "This is a valid test resource description with enough length."
    }, follow_redirects=False)
    
    u = db.query(User).filter(User.email == "adv4@test.com").first()
    assert u.helppoints_balance == 50
    
    r = db.query(Resource).filter(Resource.title == "Valid Resource For Points").first()
    
    # Login as Admin
    client.post("/login", data={"email": "admin@helplink.org", "password": "AdminDevPassword123!"})
    
    # Reject it
    client.post(f"/admin/resources/{r.id}/status", data={"status": "rejected"}, follow_redirects=False)
    
    db.refresh(u)
    assert u.helppoints_balance == 0
    
    # Check AdminAuditLog
    audit = db.query(AdminAuditLog).first()
    assert audit is not None
    assert audit.action == "UPDATE_RESOURCE_STATUS"
    assert "published to rejected" in audit.reason

def test_contributor_id_collision(client, db: Session, monkeypatch):
    import app.services.auth_service as auth_service
    
    # Mock generate_contributor_id to always return the same ID
    original_generate = auth_service.generate_contributor_id
    
    collision_count = 0
    def mock_generate():
        nonlocal collision_count
        collision_count += 1
        if collision_count == 1:
            return "HL-COLLID"
        elif collision_count == 2:
            return "HL-COLLID"  # Force collision on second user
        else:
            return f"HL-FIXED{collision_count}"
            
    monkeypatch.setattr(auth_service, "generate_contributor_id", mock_generate)
    
    # Create first user
    res1 = client.post("/register", data={"full_name": "User 1", "email": "u1@test.com", "password": "Password123!"}, follow_redirects=False)
    assert res1.status_code == 303
    
    # Create second user
    res2 = client.post("/register", data={"full_name": "User 2", "email": "u2@test.com", "password": "Password123!"}, follow_redirects=False)
    assert res2.status_code == 303  # Should succeed thanks to retry logic!
    
    u1 = db.query(User).filter(User.email == "u1@test.com").first()
    u2 = db.query(User).filter(User.email == "u2@test.com").first()
    
    assert u1.contributor_id == "HL-COLLID"
    assert u2.contributor_id == "HL-FIXED3"
    assert collision_count >= 3
