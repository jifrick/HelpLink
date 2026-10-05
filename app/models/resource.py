from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.tag import resource_tags

class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # Opportunity, Course, Scholarship, Job, Internship, Event, Support, Tool, etc.
    location: Mapped[str] = mapped_column(String(150), index=True, nullable=False, default="Remote")
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    contact: Mapped[str] = mapped_column(String(255), nullable=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(25), default="pending", index=True, nullable=False) # pending, published, rejected, archived
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Moderation
    risk_score: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="resources")
    submitter = relationship("User", back_populates="resources")
    tags = relationship("Tag", secondary=resource_tags, back_populates="resources")
    saved_by = relationship("SavedResource", back_populates="resource", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="resource", cascade="all, delete-orphan")
