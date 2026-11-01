"""Administrative User model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class User(Base):
    """Administrative or support staff user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32), default="operator", nullable=False
    )  # 'owner', 'admin', 'operator', 'viewer'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    business = relationship("Business", back_populates="users")
    assigned_conversations = relationship("Conversation", back_populates="assigned_operator")
    assigned_tickets = relationship("SupportTicket", back_populates="assigned_operator")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        Index("idx_users_business_email", "business_id", "email", unique=True),
    )
