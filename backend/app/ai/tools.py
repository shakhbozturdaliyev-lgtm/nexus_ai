"""Deterministic database-backed tools for AI function calling."""

import re
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.models.business import Business
from backend.app.models.knowledge import KnowledgeArticle
from backend.app.models.order import Order, OrderItem
from backend.app.models.product import Product, ProductVariant
from backend.app.models.ticket import SupportTicket


async def tool_search_products(
    db: AsyncSession,
    business_id: int,
    query: str,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> Dict[str, Any]:
    """Search products and variants matching keyword query and filters."""
    clean_query = query.strip().lower()
    stmt = (
        select(Product)
        .where(
            Product.business_id == business_id,
            Product.active_status.is_(True),
        )
    )
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)

    res = await db.execute(stmt)
    products = res.scalars().all()

    matched = []
    stopwords = {"bormi", "narxi", "qancha", "turadi", "va", "haqida", "mahsulot", "цена", "сколько", "стоит", "how", "much", "is"}
    query_words = [w for w in re.findall(r"[a-zA-Z0-9]+", clean_query) if w not in stopwords]

    for p in products:
        p_name = p.name.lower()
        p_brand = p.brand.lower()
        p_tokens = set(re.findall(r"[a-zA-Z0-9]+", p_name)) | set(re.findall(r"[a-zA-Z0-9]+", p_brand))

        # Check full containment or multi-token overlap
        token_match = any(w in p_tokens for w in query_words if len(w) >= 3 or not w.isdigit())

        if (
            clean_query in p_name
            or p_name in clean_query
            or clean_query in p_brand
            or token_match
        ):
            # Fetch variants
            v_res = await db.execute(
                select(ProductVariant).where(ProductVariant.product_id == p.id)
            )
            variants = v_res.scalars().all()

            v_list = []
            for v in variants:
                if min_price and float(v.price) < min_price:
                    continue
                if max_price and float(v.price) > max_price:
                    continue
                v_list.append({
                    "variant_id": v.id,
                    "sku": v.sku,
                    "storage_capacity": v.storage_capacity,
                    "color": v.color,
                    "price_uzs": float(v.price),
                    "stock_quantity": v.stock_quantity,
                    "availability_status": v.availability_status,
                })

            if v_list or (not min_price and not max_price):
                matched.append({
                    "product_id": p.id,
                    "name": p.name,
                    "brand": p.brand,
                    "description": p.description,
                    "currency": p.currency,
                    "variants": v_list,
                })

    return {
        "count": len(matched),
        "products": matched,
    }


async def tool_get_product_details(
    db: AsyncSession, business_id: int, product_id: int
) -> Dict[str, Any]:
    """Get complete specifications, variants, and stock for a product."""
    res = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.business_id == business_id,
            Product.active_status.is_(True),
        )
    )
    product = res.scalar_one_or_none()
    if not product:
        return {"error": "Product not found"}

    v_res = await db.execute(
        select(ProductVariant).where(ProductVariant.product_id == product.id)
    )
    variants = v_res.scalars().all()

    return {
        "product_id": product.id,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "currency": product.currency,
        "variants": [
            {
                "variant_id": v.id,
                "sku": v.sku,
                "storage_capacity": v.storage_capacity,
                "color": v.color,
                "price_uzs": float(v.price),
                "stock_quantity": v.stock_quantity,
                "availability_status": v.availability_status,
            }
            for v in variants
        ],
    }


async def tool_check_inventory(
    db: AsyncSession, business_id: int, product_id: int, variant_id: Optional[int] = None
) -> Dict[str, Any]:
    """Check verified real-time stock levels for product variants."""
    stmt = select(ProductVariant).join(Product).where(
        Product.id == product_id,
        Product.business_id == business_id,
    )
    if variant_id:
        stmt = stmt.where(ProductVariant.id == variant_id)

    res = await db.execute(stmt)
    variants = res.scalars().all()

    if not variants:
        return {"error": "Variant not found"}

    return {
        "product_id": product_id,
        "inventory": [
            {
                "variant_id": v.id,
                "sku": v.sku,
                "attributes": f"{v.storage_capacity or ''} {v.color or ''}".strip(),
                "stock_quantity": v.stock_quantity,
                "in_stock": v.stock_quantity > 0,
            }
            for v in variants
        ],
    }


async def tool_get_business_hours(db: AsyncSession, business_id: int) -> Dict[str, Any]:
    """Retrieve verified showroom and support operating hours."""
    res = await db.execute(select(Business).where(Business.id == business_id))
    b = res.scalar_one_or_none()
    if not b:
        return {"error": "Business profile not found"}
    return {
        "business_name": b.name,
        "timezone": b.timezone,
        "working_hours": b.working_hours,
        "contact_information": b.contact_information,
    }


async def tool_get_delivery_policy(
    db: AsyncSession, business_id: int, region: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve verified delivery rates, timelines, and thresholds."""
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.business_id == business_id,
            KnowledgeArticle.category == "delivery",
            KnowledgeArticle.is_active.is_(True),
        )
    )
    articles = res.scalars().all()
    return {
        "target_region": region or "All regions",
        "policies": [{"language": a.language, "policy": a.content} for a in articles],
    }


async def tool_get_return_policy(db: AsyncSession, business_id: int) -> Dict[str, Any]:
    """Retrieve verified return, exchange, and warranty policies."""
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.business_id == business_id,
            KnowledgeArticle.category == "return_warranty",
            KnowledgeArticle.is_active.is_(True),
        )
    )
    articles = res.scalars().all()
    return {
        "policies": [{"language": a.language, "policy": a.content} for a in articles],
    }


async def tool_get_faq_answer(
    db: AsyncSession, business_id: int, question: str
) -> Dict[str, Any]:
    """Search knowledge base FAQs for verified answers."""
    q_clean = question.strip().lower()
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.business_id == business_id,
            KnowledgeArticle.category == "faq",
            KnowledgeArticle.is_active.is_(True),
        )
    )
    faqs = res.scalars().all()

    matched = []
    for f in faqs:
        if any(token in f.title.lower() or token in f.content.lower() for token in q_clean.split()):
            matched.append({"question": f.title, "answer": f.content, "language": f.language})

    if not matched:
        matched = [{"question": f.title, "answer": f.content, "language": f.language} for f in faqs[:3]]

    return {"faqs": matched}


async def tool_get_order_status(
    db: AsyncSession,
    business_id: int,
    order_number: str,
    verified_customer_id: int,
) -> Dict[str, Any]:
    """Retrieve order status with strict customer verification."""
    clean_ord = order_number.strip().upper()
    res = await db.execute(
        select(Order).where(
            Order.order_number == clean_ord,
            Order.customer_id == verified_customer_id,
            Order.business_id == business_id,
        )
    )
    order = res.scalar_one_or_none()

    if not order:
        logger.warning(
            f"Unauthorized or non-existent order lookup attempt: '{clean_ord}' by customer ID {verified_customer_id}"
        )
        return {
            "error": "Order not found or does not belong to this customer account."
        }

    return {
        "order_number": order.order_number,
        "status": order.status,
        "total_amount_uzs": float(order.total_amount),
        "currency": order.currency,
        "created_at": order.created_at.isoformat(),
        "shipping_address": order.shipping_address,
    }


async def tool_create_support_ticket(
    db: AsyncSession,
    business_id: int,
    customer_id: int,
    category: str,
    message: str,
    conversation_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Create an escalated support ticket."""
    ticket = SupportTicket(
        business_id=business_id,
        customer_id=customer_id,
        conversation_id=conversation_id,
        category=category,
        priority="high" if category in ["complaint", "return"] else "medium",
        status="open",
    )
    db.add(ticket)
    await db.flush()
    logger.info(f"Created SupportTicket ID={ticket.id} for Customer ID={customer_id}")
    return {
        "ticket_id": ticket.id,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "message": "Support ticket created successfully.",
    }
