"""Product and ProductVariant models."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base


class Product(Base):
    """Product catalog item."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="UZS", nullable=False)
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
    business = relationship("Business", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_products_business_brand", "business_id", "brand"),
        Index("idx_products_business_name", "business_id", "name"),
    )


class ProductVariant(Base):
    """Specific SKU, attribute combination, price, and inventory count."""

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_capacity: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    attributes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    availability_status: Mapped[str] = mapped_column(
        String(32), default="in_stock", nullable=False
    )  # in_stock, low_stock, out_of_stock
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
    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")

    __table_args__ = (
        Index("idx_variants_sku", "sku"),
        Index("idx_variants_product", "product_id"),
    )
