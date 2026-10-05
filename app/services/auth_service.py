from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
import random

def generate_contributor_id() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    suffix = "".join(random.choices(chars, k=6))
    return f"HL-{suffix}"

from sqlalchemy.exc import IntegrityError

def _save_user_with_retry(db: Session, user: User) -> User:
    for attempt in range(5):
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            if "contributor_id" in str(e).lower() and attempt < 4:
                user.contributor_id = generate_contributor_id()
                continue
            raise e
    from fastapi import HTTPException
    raise HTTPException(status_code=500, detail="Unable to create account. Please try again.")
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate, role: str = "user") -> User:
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email.lower().strip(),
        full_name=user_in.full_name.strip(),
        password_hash=hashed_pwd,
        role=role,
        is_active=True,
        contributor_id=generate_contributor_id()
    )
    return _save_user_with_retry(db, user)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_supabase_uid(db: Session, supabase_uid: str) -> Optional[User]:
    return db.query(User).filter(User.supabase_uid == supabase_uid).first()

def sync_oauth_user(
    db: Session,
    supabase_uid: str,
    email: str,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None
) -> User:
    clean_email = email.lower().strip()
    
    # 1. Search by supabase_uid
    user = get_user_by_supabase_uid(db, supabase_uid)
    
    if not user:
        # 2. Search by email if not linked yet
        user = get_user_by_email(db, clean_email)
        if user:
            user.supabase_uid = supabase_uid
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user
        
        # 3. Create new HelpLink user with role="user"
        display_name = (full_name or clean_email.split("@")[0]).strip()
        user = User(
            email=clean_email,
            full_name=display_name,
            supabase_uid=supabase_uid,
            avatar_url=avatar_url,
            password_hash=None,
            role="user",
            is_active=True,
            contributor_id=generate_contributor_id()
        )
        user = _save_user_with_retry(db, user)
    else:
        # Returning user: sync avatar if updated
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)

    return user

