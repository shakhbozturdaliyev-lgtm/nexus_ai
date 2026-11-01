"""Integration tests for support operations and human handoff lifecycle."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from backend.app.bot.session import get_conversation_history, get_or_create_active_conversation, get_or_create_customer
from backend.app.services.support_service import support_service


@pytest.mark.asyncio
async def test_full_support_escalation_lifecycle(db_session):
    """Test full cycle: escalate -> ticket creation -> claim -> reply -> note -> resolve."""
    # 1. Customer initiates conversation
    cust = await get_or_create_customer(db_session, telegram_user_id=123987456, display_name="Sobir")
    conv = await get_or_create_active_conversation(db_session, cust.id)
    assert conv.status == "ai_active"

    # 2. Escalation triggers ticket
    ticket = await support_service.escalate_conversation(
        db=db_session,
        conversation_id=conv.id,
        reason="Customer requested human due to delivery delay",
        category="delivery",
        priority="high",
    )
    assert ticket.id is not None
    assert ticket.status == "open"
    assert ticket.priority == "high"
    assert conv.status == "awaiting_operator"

    # 3. Operator claims conversation
    operator_id = 2  # Nodir Karimov from seed
    claimed_conv = await support_service.claim_conversation(
        db=db_session,
        conversation_id=conv.id,
        operator_id=operator_id,
    )
    assert claimed_conv.status == "operator_active"
    assert claimed_conv.assigned_operator_id == operator_id

    # 4. Operator sends message to customer with Telegram mock
    mock_bot_app = MagicMock()
    mock_bot_app.bot = AsyncMock()
    mock_bot_app.bot.send_message = AsyncMock()

    op_msg = await support_service.send_operator_reply(
        db=db_session,
        conversation_id=conv.id,
        operator_id=operator_id,
        content="Assalomu alaykum, Sobir aka! Kurer bilan bog'landim, 30 daqiqada yetib boradi.",
        bot_application=mock_bot_app,
    )
    assert op_msg.id is not None
    assert op_msg.sender_type == "operator"
    assert op_msg.is_internal is False
    assert mock_bot_app.bot.send_message.called

    # 5. Operator adds internal note (must be invisible in customer history)
    note_msg = await support_service.add_internal_note(
        db=db_session,
        conversation_id=conv.id,
        operator_id=operator_id,
        note_content="Courier contact: +998901112233. Delivery verified.",
    )
    assert note_msg.is_internal is True

    history = await get_conversation_history(db_session, conv.id)
    history_contents = [m.content for m in history]
    assert op_msg.content in history_contents
    assert note_msg.content not in history_contents  # Strictly isolated!

    # 6. Operator resolves and closes conversation
    resolved_conv = await support_service.resolve_conversation(
        db=db_session,
        conversation_id=conv.id,
        operator_id=operator_id,
        resolution_notes="Issue resolved with courier.",
    )
    assert resolved_conv.status == "closed"
    assert resolved_conv.closed_at is not None
