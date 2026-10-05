import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

def get_supabase_client() -> Optional[Any]:
    url = settings.SUPABASE_URL
    key = settings.effective_supabase_key
    if not url or not key or not create_client:
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def get_google_auth_url(redirect_to: str) -> str:
    """Generate Supabase Google OAuth authorization URL."""
    base_url = settings.SUPABASE_URL.rstrip('/') if settings.SUPABASE_URL else ""
    if not base_url:
        raise ValueError("SUPABASE_URL is not configured in environment variables.")
    
    encoded_redirect = quote(redirect_to, safe='')
    return f"{base_url}/auth/v1/authorize?provider=google&redirect_to={encoded_redirect}"

def get_user_from_supabase_token(access_token: str) -> Optional[Dict[str, Any]]:
    """Retrieve user details from Supabase Auth using access token."""
    url = settings.SUPABASE_URL.rstrip('/') if settings.SUPABASE_URL else ""
    key = settings.effective_supabase_key
    if not url or not key:
        return None

    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {access_token}"
        }
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{url}/auth/v1/user", headers=headers)
            if res.status_code == 200:
                data = res.json()
                return {
                    "id": data.get("id"),
                    "email": data.get("email"),
                    "user_metadata": data.get("user_metadata", {}),
                }
    except Exception as e:
        logger.error(f"Error fetching Supabase user from token: {e}")

    return None

def exchange_code_for_user(code: str) -> Optional[Dict[str, Any]]:
    """
    Exchange OAuth authorization code for Supabase session and return user details.
    Tries Supabase SDK first, falling back to direct HTTP REST request.
    """
    url = settings.SUPABASE_URL.rstrip('/') if settings.SUPABASE_URL else ""
    key = settings.effective_supabase_key

    # 1. Try Supabase Python SDK
    client = get_supabase_client()
    if client:
        try:
            res = client.auth.exchange_code_for_session({"auth_code": code})
            if res and res.user:
                return {
                    "id": res.user.id,
                    "email": res.user.email,
                    "user_metadata": getattr(res.user, "user_metadata", {}) or {},
                }
        except Exception as e:
            logger.warning(f"SDK exchange_code_for_session failed, trying REST API fallback: {e}")

    # 2. Fallback REST API GoTrue token exchange
    if not url or not key:
        return None

    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }

    # Attempt PKCE and authorization_code grants
    for grant_type in ["pkce", "authorization_code"]:
        try:
            payload = {
                "auth_code": code,
                "code": code
            }
            with httpx.Client(timeout=10.0) as http_client:
                res = http_client.post(
                    f"{url}/auth/v1/token?grant_type={grant_type}",
                    json=payload,
                    headers=headers
                )
                if res.status_code == 200:
                    token_data = res.json()
                    user_data = token_data.get("user", {})
                    access_token = token_data.get("access_token")

                    if user_data and "id" in user_data:
                        return {
                            "id": user_data.get("id"),
                            "email": user_data.get("email"),
                            "user_metadata": user_data.get("user_metadata", {}),
                        }
                    elif access_token:
                        return get_user_from_supabase_token(access_token)
        except Exception as e:
            logger.error(f"REST exchange failed for grant {grant_type}: {e}")

    return None
