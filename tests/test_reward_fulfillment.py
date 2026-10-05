import pytest
from sqlalchemy.orm import Session
from app.models.gamification import Reward, RewardRedemption
from app.models.user import User

def test_reward_redemption_flow(client, db: Session):
    client.post("/register", data={"full_name": "Test User", "email": "r1@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "r1@test.com", "password": "Password123!"})
    
    user = db.query(User).filter(User.email == "r1@test.com").first()
    user.helppoints_balance = 150
    db.commit()

    reward = Reward(
        name="Test Deliverable Wallpaper",
        description="A real file",
        cost_hp=100,
        reward_type="DIGITAL_DOWNLOAD",
        status="READY",
        asset_reference="requirements.txt",
        is_active=True
    )
    db.add(reward)
    db.commit()
    
    res = client.post(f"/rewards/{reward.id}/redeem", follow_redirects=False)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "FULFILLED"
    
    db.refresh(user)
    assert user.helppoints_balance == 50
    
    res2 = client.post(f"/rewards/{reward.id}/redeem", follow_redirects=False)
    assert res2.status_code == 400
    assert "already own" in res2.json()["error"]
    
    db.refresh(user)
    assert user.helppoints_balance == 50
    
    res_dl = client.get(f"/rewards/{reward.id}/download")
    assert res_dl.status_code == 200
    assert "fastapi" in res_dl.text

def test_insufficient_points(client, db: Session):
    client.post("/register", data={"full_name": "Test User", "email": "r2@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "r2@test.com", "password": "Password123!"})
    
    user = db.query(User).filter(User.email == "r2@test.com").first()
    user.helppoints_balance = 100
    db.commit()

    reward = Reward(
        name="Expensive Reward",
        description="Costs too much",
        cost_hp=5000,
        reward_type="DIGITAL_DOWNLOAD",
        status="READY",
        asset_reference="requirements.txt",
        is_active=True
    )
    db.add(reward)
    db.commit()
    
    res = client.post(f"/rewards/{reward.id}/redeem", follow_redirects=False)
    assert res.status_code == 400
    assert "Insufficient" in res.json()["error"]
    
def test_unavailable_reward(client, db: Session):
    client.post("/register", data={"full_name": "Test User", "email": "r3@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "r3@test.com", "password": "Password123!"})
    
    user = db.query(User).filter(User.email == "r3@test.com").first()
    user.helppoints_balance = 100
    db.commit()

    reward = Reward(
        name="Fake Reward",
        description="Not ready",
        cost_hp=50,
        reward_type="DIGITAL_DOWNLOAD",
        status="DRAFT",
        is_active=True
    )
    db.add(reward)
    db.commit()
    
    res = client.post(f"/rewards/{reward.id}/redeem", follow_redirects=False)
    assert res.status_code == 400
    assert "not currently available" in res.json()["error"]

def test_unauthorized_download(client, db: Session):
    client.post("/register", data={"full_name": "Test User", "email": "r4@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "r4@test.com", "password": "Password123!"})

    reward = Reward(
        name="Secret",
        description="Secret",
        cost_hp=10,
        reward_type="DIGITAL_DOWNLOAD",
        status="READY",
        asset_reference="requirements.txt",
        is_active=True
    )
    db.add(reward)
    db.commit()
    
    res = client.get(f"/rewards/{reward.id}/download")
    assert res.status_code == 403
    
def test_path_traversal_prevention(client, db: Session):
    client.post("/register", data={"full_name": "Test User", "email": "r5@test.com", "password": "Password123!"})
    client.post("/login", data={"email": "r5@test.com", "password": "Password123!"})
    
    user = db.query(User).filter(User.email == "r5@test.com").first()
    user.helppoints_balance = 100
    db.commit()

    reward = Reward(
        name="Malicious",
        description="Hack",
        cost_hp=10,
        reward_type="DIGITAL_DOWNLOAD",
        status="READY",
        asset_reference="../../../windows/system32/cmd.exe",
        is_active=True
    )
    db.add(reward)
    db.commit()
    
    client.post(f"/rewards/{reward.id}/redeem", follow_redirects=False)
    
    res = client.get(f"/rewards/{reward.id}/download")
    assert res.status_code == 400
    assert "Invalid path" in res.text
