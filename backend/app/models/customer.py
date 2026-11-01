"""Customer model."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Customer(Base):
    """Customer entity linked to a Telegram user account."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    preferred_language: Mapped[str] = mapped_column(
        String(10), default="uz", nullable=False
    )  # 'uz', 'ru', 'en', 'uz_cyrl'
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_interaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    business = relationship("Business", back_populates="customers")
    conversations = relationship(
        "Conversation", back_populates="customer", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("SupportTicket", back_populates="customer")

    __table_args__ = (
        Index("idx_customers_business_telegram", "business_id", "telegram_user_id", unique=True),
    )
