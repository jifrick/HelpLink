import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.config import settings, Settings
from app.services.auth_service import sync_oauth_user, get_user_by_email, get_user_by_supabase_uid
from app.models.user import User

def test_google_login_initiation(client, monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://test-project.supabase.co")
    res = client.get("/auth/google", follow_redirects=False)
    assert res.status_code == 303
    assert "https://test-project.supabase.co/auth/v1/authorize?provider=google" in res.headers["location"]

def test_google_login_initiation_missing_supabase_url(client, monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "")
    res = client.get("/auth/google")
    assert res.status_code == 400
    assert "SUPABASE_URL is not configured" in res.text

def test_oauth_callback_canceled(client):
    res = client.get("/auth/callback?error=access_denied&error_description=User+canceled")
    assert res.status_code == 400
    assert "User canceled" in res.text

def test_oauth_callback_invalid_code(client, monkeypatch):
    monkeypatch.setattr("app.web.views_auth.exchange_code_for_user", lambda code: None)
    res = client.get("/auth/callback?code=invalid_code_123")
    assert res.status_code == 400
    assert "Failed to complete Google authentication" in res.text

def test_first_time_google_user_creation(db):
    supabase_uid = "g-user-uid-001"
    email = "newgoogleuser@example.com"
    full_name = "New Google User"
    avatar_url = "https://lh3.googleusercontent.com/avatar.jpg"

    user = sync_oauth_user(db, supabase_uid=supabase_uid, email=email, full_name=full_name, avatar_url=avatar_url)

    assert user.id is not None
    assert user.email == email
    assert user.full_name == full_name
    assert user.supabase_uid == supabase_uid
    assert user.avatar_url == avatar_url
    assert user.role == "user"  # CRITICAL: Must be standard user role
    assert user.password_hash is None

def test_returning_google_user_login(db):
    supabase_uid = "g-user-uid-002"
    email = "returninguser@example.com"

    # First login creates account
    u1 = sync_oauth_user(db, supabase_uid=supabase_uid, email=email, full_name="User First")
    
    # Second login reuses same account
    u2 = sync_oauth_user(db, supabase_uid=supabase_uid, email=email, full_name="User Second", avatar_url="https://new-avatar.png")

    assert u1.id == u2.id
    assert u2.avatar_url == "https://new-avatar.png"
    assert db.query(User).filter(User.email == email).count() == 1

def test_duplicate_account_prevention_existing_email(db):
    # Existing user registered via email/password
    existing_user = User(
        email="existingemail@example.com",
        full_name="Email Register User",
        password_hash="somehash",
        role="user"
    )
    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)

    # User logs in via Google with same email
    supabase_uid = "g-user-uid-003"
    linked_user = sync_oauth_user(db, supabase_uid=supabase_uid, email="existingemail@example.com", full_name="Google Name")

    assert linked_user.id == existing_user.id
    assert linked_user.supabase_uid == supabase_uid
    assert db.query(User).filter(User.email == "existingemail@example.com").count() == 1

def test_google_user_cannot_become_admin_automatically(db):
    supabase_uid = "g-user-uid-admin-attempt"
    email = "randomuser@example.com"

    user = sync_oauth_user(db, supabase_uid=supabase_uid, email=email)
    assert user.role == "user"
    assert user.role != "admin"

def test_oauth_callback_successful_flow(client, monkeypatch):
    mock_supabase_user = {
        "id": "supabase-uid-success-123",
        "email": "google.success@example.com",
        "user_metadata": {
            "full_name": "Google Success User",
            "avatar_url": "https://lh3.google.com/photo.jpg"
        }
    }
    monkeypatch.setattr("app.web.views_auth.exchange_code_for_user", lambda code: mock_supabase_user)

    res = client.get("/auth/callback?code=valid_test_code_123", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/dashboard"
    assert "helplink_session" in res.cookies

def test_oauth_callback_post_successful_flow(client, monkeypatch):
    mock_supabase_user = {
        "id": "supabase-uid-post-123",
        "email": "google.post@example.com",
        "user_metadata": {
            "name": "Google Post User",
            "picture": "https://lh3.google.com/picture.jpg"
        }
    }
    monkeypatch.setattr("app.web.views_auth.get_user_from_supabase_token", lambda token: mock_supabase_user)

    res = client.post("/auth/callback", data={"access_token": "valid_token_abc"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/dashboard"
    assert "helplink_session" in res.cookies

def test_logout_clears_session(client):
    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/"
    # Verify cookie expires or is empty
    assert "helplink_session" in res.headers.get("set-cookie", "")
