"""Comprehensive End-to-End Scenario Tests (Scenarios A through F from Phase 10)."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch
import pytest
from backend.app.ai.orchestrator import AIOrchestrator
from backend.app.bot.session import (
    get_or_create_active_conversation,
    get_or_create_customer,
    save_message,
)
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.services.support_service import support_service


@pytest.mark.asyncio
async def test_scenario_a_product_inquiry(db_session):
    """Scenario A: Customer asks about Samsung Galaxy A16 in Uzbek; agent searches DB and returns verified price in UZS."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=10101, display_name="Ali")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Samsung Galaxy A16 narxi qancha?",
        lang="uz",
    )

    assert "Samsung Galaxy A16" in response.text
    # Verified price from seed is 2,450,000 UZS
    assert "2 450 000" in response.text or "2450000" in response.text
    assert "UZS" in response.text
    assert response.escalated_to_human is False


@pytest.mark.asyncio
async def test_scenario_b_missing_price_hallucination_prevention(db_session):
    """Scenario B: Customer asks about PlayStation 6 (not in catalog); agent does NOT invent price, states unverified."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=20202, display_name="Vali")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="PlayStation 6 bormi va narxi qancha?",
        lang="uz",
    )

    # Must honestly report unconfirmed/not found rather than making up a price
    assert "tasdiqlangan narx" in response.text.lower() or "topilmadi" in response.text.lower()
    # Must offer human operator assistance
    assert "operator" in response.text.lower()


@pytest.mark.asyncio
async def test_scenario_c_multilingual_conversation(db_session):
    """Scenario C: Customer begins in Uzbek, then switches to Russian mid-dialogue."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=30303, display_name="Aziz")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    # Turn 1 in Uzbek
    turn1 = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Yetkazib berish shartlari qanday?",
        lang="uz",
    )
    assert "Yetkazib berish" in turn1.text or "Toshkent" in turn1.text

    # Turn 2 in Russian
    turn2 = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="А сколько стоит доставка в Самарканд?",
        lang="ru",
    )
    assert "Доставка" in turn2.text or "доставка" in turn2.text or "сум" in turn2.text


@pytest.mark.asyncio
async def test_scenario_d_human_escalation_workflow(db_session):
    """Scenario D: Customer requests a human operator; ticket created, status set to awaiting_operator, AI silenced."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=40404, display_name="Nodira")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Menga jonli inson kerak, operator bilan gaplashmoqchiman",
        lang="uz",
    )

    assert response.escalated_to_human is True
    # Verify ticket was generated
    assert len(response.tool_calls_made) >= 1
    ticket_call = next(tc for tc in response.tool_calls_made if tc["tool"] == "create_support_ticket")
    assert ticket_call["result"]["status"] == "open"


@pytest.mark.asyncio
async def test_scenario_e_unauthorized_order_lookup(db_session):
    """Scenario E: Customer attempts to look up an order owned by a different customer; access is refused."""
    orch = AIOrchestrator()

    # Create Alice (owner) and Eve (attacker)
    alice = Customer(business_id=1, telegram_user_id=50501, display_name="Alice")
    eve = Customer(business_id=1, telegram_user_id=50502, display_name="Eve")
    db_session.add_all([alice, eve])
    await db_session.flush()

    # Alice's order
    alice_order = Order(
        business_id=1,
        customer_id=alice.id,
        order_number="ORD-99999",
        status="shipping",
        total_amount=Decimal("12800000.00"),
        currency="UZS",
    )
    db_session.add(alice_order)
    await db_session.flush()

    eve_conv = await get_or_create_active_conversation(db_session, eve.id)

    # Eve tries to query Alice's order
    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=eve.id,
        conversation_id=eve_conv.id,
        user_message="Mening buyurtmam qayerda? Raqami ORD-99999",
        lang="uz",
    )

    # Eve must NOT receive Alice's order details!
    assert "12 800 000" not in response.text
    assert "topilmadi" in response.text.lower() or "tegishli emas" in response.text.lower()


@pytest.mark.asyncio
async def test_scenario_f_gemini_outage_resilience(db_session):
    """Scenario F: Gemini API times out or throws 503; system gracefully falls back without crashing."""
    orch = AIOrchestrator()
    cust = await get_or_create_customer(db_session, telegram_user_id=60606, display_name="Timur")
    conv = await get_or_create_active_conversation(db_session, cust.id)

    # Force mock a broken Gemini engine that raises an exception
    mock_broken_gemini = AsyncMock()
    mock_broken_gemini.generate_response.side_effect = RuntimeError("Gemini 503 Service Unavailable")
    orch.gemini_engine = mock_broken_gemini

    # Must catch and fall back seamlessly to offline engine
    response = await orch.process_message(
        db=db_session,
        business_id=1,
        customer_id=cust.id,
        conversation_id=conv.id,
        user_message="Samsung A16 narxi qancha?",
        lang="uz",
    )

    assert response is not None
    assert "Samsung Galaxy A16" in response.text
    assert "2 450 000" in response.text or "2450000" in response.text
