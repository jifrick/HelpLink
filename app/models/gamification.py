from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class PointTransaction(Base):
    __tablename__ = "point_transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. RESOURCE_APPROVED, BONUS, PENALTY, REDEMPTION
    reference_type: Mapped[str] = mapped_column(String(50), nullable=True) # e.g. resource, report
    reference_id: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    user = relationship("User", foreign_keys=[user_id])

class FraudEvent(Base):
    __tablename__ = "fraud_events"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: Mapped[int] = mapped_column(default=0, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=True)
    action_taken: Mapped[str] = mapped_column(String(50), nullable=True)
    
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    resolved_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    resource = relationship("Resource", foreign_keys=[resource_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

class ModerationEvent(Base):
    __tablename__ = "moderation_events"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    automated_decision: Mapped[str] = mapped_column(String(50), nullable=False) # APPROVED, HOLD, REJECTED
    risk_score: Mapped[int] = mapped_column(default=0, nullable=False)
    checks_performed: Mapped[dict] = mapped_column(JSON, nullable=True)
    reason_codes: Mapped[dict] = mapped_column(JSON, nullable=True)
    final_status: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

class Badge(Base):
    __tablename__ = "badges"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(100), nullable=False)
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)
    threshold: Mapped[int] = mapped_column(default=0, nullable=False)
    
class UserBadge(Base):
    __tablename__ = "user_badges"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    user = relationship("User", foreign_keys=[user_id])
    badge = relationship("Badge", foreign_keys=[badge_id])

class Reward(Base):
    __tablename__ = "rewards"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost_hp: Mapped[int] = mapped_column(nullable=False)
    reward_type: Mapped[str] = mapped_column(String(50), nullable=False) # DIGITAL_DOWNLOAD, PHYSICAL, BADGE, ROLE
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reward_id: Mapped[int] = mapped_column(ForeignKey("rewards.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False) # PENDING, APPROVED, FULFILLED, CANCELLED
    redemption_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", foreign_keys=[user_id])
    reward = relationship("Reward", foreign_keys=[reward_id])
