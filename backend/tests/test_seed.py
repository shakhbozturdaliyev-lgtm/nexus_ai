"""Integration tests verifying database seed data."""

import pytest
from sqlalchemy import select
from backend.app.models.business import Business
from backend.app.models.category import Category
from backend.app.models.knowledge import KnowledgeArticle
from backend.app.models.product import Product, ProductVariant
from backend.app.models.user import User


@pytest.mark.asyncio
async def test_seeded_business(db_session):
    """Verify Demo Electronics business record."""
    result = await db_session.execute(select(Business).where(Business.id == 1))
    business = result.scalar_one_or_none()

    assert business is not None
    assert business.name == "Demo Electronics"
    assert business.timezone == "Asia/Tashkent"
    assert business.primary_language == "uz"


@pytest.mark.asyncio
async def test_seeded_categories_and_products(db_session):
    """Verify demo catalog products, variants, prices, and stock."""
    # Check Categories
    cats = (await db_session.execute(select(Category))).scalars().all()
    cat_slugs = [c.slug for c in cats]
    assert "smartphones" in cat_slugs
    assert "laptops" in cat_slugs

    # Check Samsung Galaxy A16
    result = await db_session.execute(
        select(Product).where(Product.name == "Samsung Galaxy A16")
    )
    samsung = result.scalar_one_or_none()
    assert samsung is not None
    assert samsung.brand == "Samsung"
    assert samsung.currency == "UZS"

    # Check Samsung Variants
    variants_res = await db_session.execute(
        select(ProductVariant).where(ProductVariant.product_id == samsung.id)
    )
    variants = variants_res.scalars().all()
    assert len(variants) >= 2

    # Check 128GB variant price = 2,450,000 UZS
    v128 = next((v for v in variants if v.storage_capacity == "128 GB"), None)
    assert v128 is not None
    assert v128.price == 2450000.00
    assert v128.stock_quantity == 15
    assert v128.sku == "SAM-A16-128-BLK"


@pytest.mark.asyncio
async def test_seeded_knowledge_base(db_session):
    """Verify multilingual knowledge base articles."""
    articles = (await db_session.execute(select(KnowledgeArticle))).scalars().all()
    assert len(articles) >= 6

    # Verify delivery policy exists in Uzbek, Russian, and English
    delivery_articles = [a for a in articles if a.category == "delivery"]
    languages = {a.language for a in delivery_articles}
    assert "uz" in languages
    assert "ru" in languages
    assert "en" in languages


@pytest.mark.asyncio
async def test_seeded_users(db_session):
    """Verify default admin and operator accounts."""
    users = (await db_session.execute(select(User))).scalars().all()
    emails = {u.email for u in users}
    assert "admin@demoelectronics.uz" in emails
    assert "operator@demoelectronics.uz" in emails
