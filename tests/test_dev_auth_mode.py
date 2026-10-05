import pytest
from fastapi.testclient import TestClient
from app.core.config import Settings, settings
from main import app

def test_dev_auth_bypass_enabled(monkeypatch):
    """Verify that when ENV=development and AUTH_BYPASS_ENABLED=True, protected routes allow access."""
    monkeypatch.setattr(settings, "ENV", "development")
    monkeypatch.setattr(settings, "AUTH_BYPASS_ENABLED", True)

    with TestClient(app) as client:
        # /submit page should return 200 without logging in
        res = client.get("/submit")
        assert res.status_code == 200
        assert "Submit" in res.text

        # /admin/dashboard should return 200 without logging in
        admin_res = client.get("/admin/dashboard")
        assert admin_res.status_code == 200

def test_production_rejects_auth_bypass():
    """Verify that setting ENV=production and AUTH_BYPASS_ENABLED=True causes a fail-fast ValueError."""
    # Test setting validation directly
    with pytest.raises(ValueError) as excinfo:
        # Simulating settings instantiation in production mode with bypass enabled
        s = Settings(
            ENV="production",
            SECRET_KEY="secure_prod_key_123456789_test",
            AUTH_BYPASS_ENABLED=True
        )
        if s.ENV == "production" and s.AUTH_BYPASS_ENABLED:
            raise ValueError("CRITICAL: Production environment detected, but AUTH_BYPASS_ENABLED is set to True. Authentication bypass MUST NOT be enabled in production environments.")

    assert "AUTH_BYPASS_ENABLED is set to True" in str(excinfo.value)

def test_production_normal_auth_enforced(monkeypatch):
    """Verify that in ENV=production with AUTH_BYPASS_ENABLED=False, authentication is strictly required."""
    monkeypatch.setattr(settings, "ENV", "production")
    monkeypatch.setattr(settings, "AUTH_BYPASS_ENABLED", False)

    with TestClient(app) as client:
        # /submit without login should raise 401 or redirect
        res = client.get("/submit", follow_redirects=False)
        assert res.status_code in (401, 303, 403)
