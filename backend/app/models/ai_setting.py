"""AISetting model."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class AISetting(Base):
    """Business-level AI configuration parameters."""

    __tablename__ = "ai_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    model_name: Mapped[str] = mapped_column(
        String(64), default="gemini-2.5-flash", nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=800, nullable=False)
    context_window_turns: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    tool_call_limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    system_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    escalation_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    fallback_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    business = relationship("Business", back_populates="ai_settings")
