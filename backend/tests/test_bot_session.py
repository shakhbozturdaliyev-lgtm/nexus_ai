"""Integration tests for customer session and conversation persistence."""

import pytest
from backend.app.bot.session import (
    get_conversation_history,
    get_or_create_active_conversation,
    get_or_create_customer,
    save_message,
    update_customer_language,
)


@pytest.mark.asyncio
async def test_customer_lifecycle(db_session):
    """Test creating and retrieving customer by Telegram ID."""
    telegram_id = 998901234
    customer = await get_or_create_customer(
        db_session,
        telegram_user_id=telegram_id,
        display_name="Anvar Aliyev",
        language_code="uz-UZ",
    )
    assert customer.id is not None
    assert customer.telegram_user_id == telegram_id
    assert customer.preferred_language == "uz"

    # Subsequent retrieval returns the same customer
    retrieved = await get_or_create_customer(
        db_session,
        telegram_user_id=telegram_id,
    )
    assert retrieved.id == customer.id

    # Update language preference
    await update_customer_language(db_session, customer.id, "ru")
    retrieved_after = await get_or_create_customer(
        db_session,
        telegram_user_id=telegram_id,
    )
    assert retrieved_after.preferred_language == "ru"


@pytest.mark.asyncio
async def test_conversation_and_messages(db_session):
    """Test active conversation creation and message logging."""
    customer = await get_or_create_customer(
        db_session,
        telegram_user_id=888777666,
        display_name="Dilshod",
    )
    conv = await get_or_create_active_conversation(db_session, customer.id)
    assert conv.id is not None
    assert conv.status == "ai_active"

    # Add messages
    m1 = await save_message(
        db_session,
        conversation_id=conv.id,
        sender_type="customer",
        content="Salom! Samsung A16 bormi?",
    )
    m2 = await save_message(
        db_session,
        conversation_id=conv.id,
        sender_type="ai",
        content="Ha, mavjud. 128 GB narxi 2,450,000 UZS.",
    )
    # Add internal note (should not be in customer history)
    m3 = await save_message(
        db_session,
        conversation_id=conv.id,
        sender_type="operator",
        content="Internal note: Verified stock in warehouse 2",
        is_internal=True,
    )

    history = await get_conversation_history(db_session, conv.id)
    assert len(history) == 2
    contents = [m.content for m in history]
    assert "Salom! Samsung A16 bormi?" in contents
    assert "Ha, mavjud. 128 GB narxi 2,450,000 UZS." in contents
    assert "Internal note: Verified stock in warehouse 2" not in contents
