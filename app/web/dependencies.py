from typing import Optional
from urllib.parse import urlparse
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.services.auth_service import get_user_by_id
from app.models.user import User

from app.core.config import settings

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Retrieve logged-in user from HTTP-only session cookie or Bearer token header."""
    token = request.cookies.get("helplink_session")
    
    # Priority: Only check Authorization header if cookie is NOT present
    auth_header = request.headers.get("Authorization")
    if not token and auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                user_id = int(payload["sub"])
                user = get_user_by_id(db, user_id)
                if user and user.is_active:
                    return user
            except ValueError:
                pass

    # Development-only authentication bypass
    if settings.ENV == "development" and settings.AUTH_BYPASS_ENABLED:
        dev_admin = db.query(User).filter(User.role == "admin").first()
        if dev_admin:
            return dev_admin
        return User(
            id=999999,
            email="dev.admin@helplink.local",
            full_name="Dev Admin User",
            role="admin",
            is_active=True
        )

    return None

def require_current_user(current_user: Optional[User] = Depends(get_current_user_from_cookie)) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

def require_admin_user(current_user: User = Depends(require_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def validate_csrf_and_origin(request: Request) -> None:
    """
    CSRF Defense: Validates Origin and Referer headers for state-changing HTTP methods
    (POST, PUT, PATCH, DELETE) to reject cross-origin requests.
    """
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")

        expected_host = request.headers.get("Host") or request.base_url.netloc

        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.netloc and parsed_origin.netloc != expected_host:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cross-origin request rejected (CSRF Protection)"
                )
        elif referer:
            parsed_referer = urlparse(referer)
            if parsed_referer.netloc and parsed_referer.netloc != expected_host:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cross-origin request rejected (CSRF Protection)"
                )
