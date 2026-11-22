"""Tests for interactive order placement and free consultation capabilities."""

import pytest
from backend.app.ai.orchestrator import AIOrchestrator
from backend.app.ai.tools import tool_create_order
from backend.app.bot.session import (
    get_or_create_active_conversation,
    get_or_create_customer,
)
from backend.app.models.order import Order


@pytest.mark.asyncio
async def test_free_consultation_recommendations(db_session):
    """Test AI advisor recommends suitable devices when asked open-endedly."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=888111, display_name="Consult User")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Menga yaxshi telefon maslahat bering",
        lang="uz",
    )
    assert response is not None
    assert "Samsung Galaxy" in response.text or "iPhone" in response.text
    assert "UZS" in response.text


@pytest.mark.asyncio
async def test_order_placement_flow(db_session):
    """Test end-to-end interactive order placement via Telegram AI."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=888222, display_name="Buyer User")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    # 1. Express buy intent
    r1 = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Samsung S23 Ultra sotib olmoqchiman",
        lang="uz",
    )
    assert "Telefon raqamingiz" in r1.text or "buyurtma" in r1.text

    # 2. Provide contact details to execute order
    r2 = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="+998901112233, Toshkent shahar Yunusobod 4-mavze 10-uy",
        lang="uz",
    )
    assert "Buyurtmangiz muvaffaqiyatli qabul qilindi" in r2.text
    assert "ORD-" in r2.text
    assert len(r2.tool_calls_made) >= 1
    assert r2.tool_calls_made[0]["tool"] == "create_order"
