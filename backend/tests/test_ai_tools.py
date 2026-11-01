"""Integration tests for database-backed AI tools."""

from decimal import Decimal
import pytest
from backend.app.ai.tools import (
    tool_check_inventory,
    tool_create_support_ticket,
    tool_get_business_hours,
    tool_get_delivery_policy,
    tool_get_faq_answer,
    tool_get_order_status,
    tool_get_product_details,
    tool_get_return_policy,
    tool_search_products,
)
from backend.app.models.customer import Customer
from backend.app.models.order import Order


@pytest.mark.asyncio
async def test_tool_search_products(db_session):
    """Test searching catalog products by name and brand."""
    # Search Samsung
    res = await tool_search_products(db_session, business_id=1, query="Samsung A16")
    assert res["count"] >= 1
    p = res["products"][0]
    assert p["name"] == "Samsung Galaxy A16"
    assert len(p["variants"]) >= 2

    # Verify verified price in UZS
    prices = [v["price_uzs"] for v in p["variants"]]
    assert 2450000.0 in prices


@pytest.mark.asyncio
async def test_tool_check_inventory(db_session):
    """Test inventory check returns accurate stock counts."""
    # Search Samsung to get ID
    search_res = await tool_search_products(db_session, business_id=1, query="Samsung")
    p_id = search_res["products"][0]["product_id"]

    inv_res = await tool_check_inventory(db_session, business_id=1, product_id=p_id)
    assert "inventory" in inv_res
    assert len(inv_res["inventory"]) >= 2
    for item in inv_res["inventory"]:
        assert item["stock_quantity"] > 0
        assert item["in_stock"] is True


@pytest.mark.asyncio
async def test_tool_business_hours_and_policies(db_session):
    """Test business hours and policy retrieval."""
    hours = await tool_get_business_hours(db_session, business_id=1)
    assert hours["timezone"] == "Asia/Tashkent"
    assert "working_hours" in hours

    delivery = await tool_get_delivery_policy(db_session, business_id=1)
    assert len(delivery["policies"]) >= 3

    returns = await tool_get_return_policy(db_session, business_id=1)
    assert len(returns["policies"]) >= 3


@pytest.mark.asyncio
async def test_tool_order_status_customer_verification(db_session):
    """Verify order lookup requires strict customer ownership verification."""
    # Create test customer and order
    cust1 = Customer(business_id=1, telegram_user_id=11111, display_name="Owner Cust")
    cust2 = Customer(business_id=1, telegram_user_id=22222, display_name="Snooper Cust")
    db_session.add_all([cust1, cust2])
    await db_session.flush()

    order = Order(
        business_id=1,
        customer_id=cust1.id,
        order_number="ORD-77777",
        status="shipping",
        total_amount=Decimal("2450000.00"),
        currency="UZS",
    )
    db_session.add(order)
    await db_session.flush()

    # Legitimate customer lookup succeeds
    valid_res = await tool_get_order_status(
        db_session,
        business_id=1,
        order_number="ORD-77777",
        verified_customer_id=cust1.id,
    )
    assert valid_res["order_number"] == "ORD-77777"
    assert valid_res["status"] == "shipping"
    assert valid_res["total_amount_uzs"] == 2450000.0

    # Cross-customer unauthorized lookup is rejected
    invalid_res = await tool_get_order_status(
        db_session,
        business_id=1,
        order_number="ORD-77777",
        verified_customer_id=cust2.id,
    )
    assert "error" in invalid_res
