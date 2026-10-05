from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.templates import templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.services.auth_service import authenticate_user, create_user, get_user_by_email, sync_oauth_user
from app.core.security import create_access_token
from app.core.supabase import get_google_auth_url, exchange_code_for_user, get_user_from_supabase_token
from app.web.dependencies import get_current_user_from_cookie
from app.models.user import User

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_form(
    request: Request,
    next: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"current_user": None, "next": next or "", "error": None}
    )

@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "current_user": None,
                "email": email,
                "next": next or "",
                "error": "Invalid email or password. Please try again."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    redirect_url = next if (next and next.startswith("/") and not next.startswith("//")) else ("/" if user.role != "admin" else "/admin")
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    token = create_access_token(user.id)
    response.set_cookie(
        key="helplink_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return response

@router.get("/register", response_class=HTMLResponse)
def register_form(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_from_cookie)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"current_user": None, "error": None}
    )

@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "current_user": None,
                "full_name": full_name,
                "email": email,
                "error": "Password must be at least 6 characters long."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    existing_user = get_user_by_email(db, email)
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "current_user": None,
                "full_name": full_name,
                "email": email,
                "error": "An account with this email address already exists."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user_in = UserCreate(email=email, full_name=full_name, password=password)
    user = create_user(db, user_in, role="user")

    response = RedirectResponse(url="/submit?registered=true", status_code=status.HTTP_303_SEE_OTHER)
    token = create_access_token(user.id)
    response.set_cookie(
        key="helplink_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return response

@router.get("/auth/google")
def auth_google(request: Request, next: Optional[str] = None):
    """Initiate Supabase Google OAuth flow."""
    redirect_url = str(request.url_for("auth_callback"))
    if not redirect_url.startswith("http"):
        redirect_url = f"{request.base_url}auth/callback"
        
    try:
        auth_url = get_google_auth_url(redirect_to=redirect_url)
        return RedirectResponse(url=auth_url, status_code=status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "current_user": None,
                "error": f"Google Sign-In configuration error: {str(e)}"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.get("/auth/callback", name="auth_callback", response_class=HTMLResponse)
def auth_callback_get(
    request: Request,
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    next: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth GET callback from Supabase Auth."""
    if error or error_description:
        err_msg = error_description or error or "Google sign in was canceled or failed."
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"current_user": None, "error": err_msg},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not code:
        return templates.TemplateResponse(
            request=request,
            name="auth/callback.html",
            context={"current_user": None, "next": next or "/dashboard"}
        )

    supabase_user = exchange_code_for_user(code)
    if not supabase_user or "email" not in supabase_user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "current_user": None,
                "error": "Failed to complete Google authentication with Supabase. Please try again."
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    email = supabase_user["email"]
    supabase_uid = supabase_user["id"]
    user_metadata = supabase_user.get("user_metadata", {})
    full_name = user_metadata.get("full_name") or user_metadata.get("name")
    avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")

    user = sync_oauth_user(
        db=db,
        supabase_uid=supabase_uid,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url
    )

    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"current_user": None, "error": "Your account has been deactivated."},
            status_code=status.HTTP_403_FORBIDDEN
        )

    target_url = next if (next and next.startswith("/") and not next.startswith("//")) else ("/admin" if user.role == "admin" else "/dashboard")
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    token = create_access_token(user.id)
    response.set_cookie(
        key="helplink_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return response

@router.post("/auth/callback", response_class=HTMLResponse)
def auth_callback_post(
    request: Request,
    access_token: Optional[str] = Form(None),
    next: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Handle client-side token POST callback."""
    if not access_token:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"current_user": None, "error": "Invalid authentication callback payload."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    supabase_user = get_user_from_supabase_token(access_token)
    if not supabase_user or "email" not in supabase_user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"current_user": None, "error": "Invalid or expired Supabase token."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    email = supabase_user["email"]
    supabase_uid = supabase_user["id"]
    user_metadata = supabase_user.get("user_metadata", {})
    full_name = user_metadata.get("full_name") or user_metadata.get("name")
    avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")

    user = sync_oauth_user(
        db=db,
        supabase_uid=supabase_uid,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url
    )

    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"current_user": None, "error": "Your account has been deactivated."},
            status_code=status.HTTP_403_FORBIDDEN
        )

    target_url = next if (next and next.startswith("/") and not next.startswith("//")) else ("/admin" if user.role == "admin" else "/dashboard")
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    token = create_access_token(user.id)
    response.set_cookie(
        key="helplink_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="helplink_session")
    return response

