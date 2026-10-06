from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    supabase_uid: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    role: Mapped[str] = mapped_column(String(25), default="user", nullable=False)  # 'user', 'admin'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    # Gamification & Moderation fields
    contributor_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    helppoints_balance: Mapped[int] = mapped_column(default=0, nullable=False)
    lifetime_helppoints: Mapped[int] = mapped_column(default=0, nullable=False)
    level: Mapped[str] = mapped_column(String(50), default="New Contributor", nullable=False)
    trust_score: Mapped[int] = mapped_column(default=50, nullable=False)  # 0-100, 50 is neutral
    fraud_risk_score: Mapped[int] = mapped_column(default=0, nullable=False) # 0-100, 0 is no risk
    account_status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False) # ACTIVE, WARNING, RESTRICTED, SUSPENDED, BANNED

    # Relationships
    resources = relationship("Resource", back_populates="submitter", cascade="all, delete-orphan")
    saved_resources = relationship("SavedResource", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
