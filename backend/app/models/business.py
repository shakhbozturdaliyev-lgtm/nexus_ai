"""Business tenant model."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Business(Base):
    """Multi-tenant root organization entity."""

    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_language: Mapped[str] = mapped_column(String(10), default="uz", nullable=False)
    supported_languages: Mapped[dict] = mapped_column(JSON, default=lambda: ["uz", "ru", "en"])
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent", nullable=False)
    contact_information: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    working_hours: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    active_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    # Relationships
    users = relationship("User", back_populates="business", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="business", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="business", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="business", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="business", cascade="all, delete-orphan")
    tickets = relationship("SupportTicket", back_populates="business", cascade="all, delete-orphan")
    knowledge_articles = relationship("KnowledgeArticle", back_populates="business", cascade="all, delete-orphan")
    ai_settings = relationship("AISetting", back_populates="business", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="business", cascade="all, delete-orphan")
