"""Integration tests for Telegram bot update handlers."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from telegram import Update, User as TgUser, Message as TgMessage, CallbackQuery
from backend.app.bot.handlers import (
    callback_query_handler,
    help_handler,
    start_handler,
    text_message_handler,
)


@pytest.fixture
def mock_tg_user():
    user = MagicMock(spec=TgUser)
    user.id = 5551234
    user.full_name = "Test User"
    user.username = "test_user"
    user.language_code = "uz"
    return user


@pytest.fixture
def mock_update(mock_tg_user):
    update = MagicMock(spec=Update)
    update.effective_user = mock_tg_user
    msg = AsyncMock(spec=TgMessage)
    msg.message_id = 101
    msg.reply_text = AsyncMock()
    update.message = msg
    return update


@pytest.mark.asyncio
async def test_start_handler(mock_update, db_session):
    """Test /start triggers greeting, main menu, and language picker."""
    context = MagicMock()
    await start_handler(mock_update, context)

    # Verify reply_text was called
    assert mock_update.message.reply_text.call_count >= 2
    # Check that greeting was sent
    first_call_args = mock_update.message.reply_text.call_args_list[0]
    assert "Demo Electronics" in first_call_args[0][0]


@pytest.mark.asyncio
async def test_help_handler(mock_update, db_session):
    """Test /help command outputs instructions."""
    context = MagicMock()
    await help_handler(mock_update, context)

    assert mock_update.message.reply_text.called
    call_text = mock_update.message.reply_text.call_args[0][0]
    assert "/start" in call_text
    assert "/help" in call_text


@pytest.mark.asyncio
async def test_language_callback(mock_update, db_session):
    """Test inline button callback to switch language to Russian."""
    query = AsyncMock(spec=CallbackQuery)
    query.data = "lang:ru"
    query.answer = AsyncMock()
    query_msg = AsyncMock()
    query.message = query_msg
    mock_update.callback_query = query

    context = MagicMock()
    await callback_query_handler(mock_update, context)

    assert query.answer.called
    assert query_msg.reply_text.called
    call_text = query_msg.reply_text.call_args[0][0]
    assert "русский" in call_text.lower()


@pytest.mark.asyncio
async def test_text_product_inquiry(mock_update, db_session):
    """Test natural language inquiry for Samsung A16 returns verified prices."""
    mock_update.message.text = "Samsung A16 narxi qancha?"
    context = MagicMock()

    await text_message_handler(mock_update, context)

    assert mock_update.message.reply_text.called
    reply = mock_update.message.reply_text.call_args[0][0]
    # Must report verified database price
    assert "Samsung Galaxy A16" in reply
    assert "2 450 000" in reply or "2450000" in reply
    assert "UZS" in reply
