"""Conversation and Message models."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Conversation(Base):
    """Customer support dialogue session."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default="ai_active", nullable=False
    )  # 'ai_active', 'awaiting_operator', 'operator_active', 'closed'
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    business = relationship("Business", back_populates="conversations")
    customer = relationship("Customer", back_populates="conversations")
    assigned_operator = relationship("User", back_populates="assigned_conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    tickets = relationship("SupportTicket", back_populates="conversation")

    __table_args__ = (
        Index("idx_conversations_business_status", "business_id", "status"),
        Index("idx_conversations_customer", "customer_id"),
    )


class Message(Base):
    """Individual interaction within a conversation."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # 'customer', 'ai', 'operator', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(32), default="text", nullable=False
    )  # 'text', 'button_click', 'handoff', 'note'
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    is_internal: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # True = hidden from customer
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_conversation_date", "conversation_id", "created_at"),
    )
