"""SupportTicket model."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class SupportTicket(Base):
    """Customer escalation support ticket."""

    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # product, delivery, return, complaint, general
    priority: Mapped[str] = mapped_column(
        String(32), default="medium", nullable=False
    )  # low, medium, high, urgent
    status: Mapped[str] = mapped_column(
        String(32), default="open", nullable=False
    )  # open, in_progress, resolved, closed
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    business = relationship("Business", back_populates="tickets")
    customer = relationship("Customer", back_populates="tickets")
    conversation = relationship("Conversation", back_populates="tickets")
    assigned_operator = relationship("User", back_populates="assigned_tickets")

    __table_args__ = (
        Index("idx_tickets_business_status", "business_id", "status"),
        Index("idx_tickets_priority", "priority"),
    )
