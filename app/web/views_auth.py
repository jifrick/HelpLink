from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.services.auth_service import authenticate_user, create_user, get_user_by_email
from app.core.security import create_access_token
from app.web.dependencies import get_current_user_from_cookie
from app.models.user import User

templates = Jinja2Templates(directory="app/templates")

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

    redirect_url = next if (next and next.startswith("/")) else ("/" if user.role != "admin" else "/admin")
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

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="helplink_session")
    return response
