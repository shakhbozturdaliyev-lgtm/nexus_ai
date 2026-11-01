"""Customer conversation session and state management."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.conversation import Conversation, Message
from backend.app.models.customer import Customer


async def get_or_create_customer(
    db: AsyncSession,
    telegram_user_id: int,
    display_name: Optional[str] = None,
    language_code: Optional[str] = None,
    business_id: int = settings.default_business_id,
) -> Customer:
    """Retrieve existing customer or create a new customer record."""
    result = await db.execute(
        select(Customer).where(
            Customer.business_id == business_id,
            Customer.telegram_user_id == telegram_user_id,
        )
    )
    customer = result.scalar_one_or_none()

    if customer:
        customer.last_interaction_at = datetime.now(timezone.utc)
        if display_name and customer.display_name != display_name:
            customer.display_name = display_name
        return customer

    # Resolve default language preference from Telegram user language code
    initial_lang = "uz"
    if language_code:
        lang_prefix = language_code.lower().split("-")[0]
        if lang_prefix in ["ru", "en"]:
            initial_lang = lang_prefix

    customer = Customer(
        business_id=business_id,
        telegram_user_id=telegram_user_id,
        preferred_language=initial_lang,
        display_name=display_name or f"User {telegram_user_id}",
    )
    db.add(customer)
    await db.flush()
    logger.info(f"Created new customer ID={customer.id} for Telegram ID={telegram_user_id}")
    return customer


async def update_customer_language(
    db: AsyncSession, customer_id: int, language: str
) -> None:
    """Update customer's preferred communication language."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if customer:
        customer.preferred_language = language
        await db.flush()


async def get_or_create_active_conversation(
    db: AsyncSession, customer_id: int, business_id: int = settings.default_business_id
) -> Conversation:
    """Get open conversation for customer or create a new one."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.business_id == business_id,
            Conversation.customer_id == customer_id,
            Conversation.status.in_(["ai_active", "awaiting_operator", "operator_active"]),
        )
        .order_by(Conversation.created_at.desc())
    )
    conversation = result.scalars().first()

    if conversation:
        return conversation

    conversation = Conversation(
        business_id=business_id,
        customer_id=customer_id,
        status="ai_active",
    )
    db.add(conversation)
    await db.flush()
    logger.info(f"Created new conversation ID={conversation.id} for customer ID={customer_id}")
    return conversation


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    sender_type: str,
    content: str,
    message_type: str = "text",
    telegram_message_id: Optional[int] = None,
    is_internal: bool = False,
) -> Message:
    """Persist conversation message."""
    message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        content=content,
        message_type=message_type,
        telegram_message_id=telegram_message_id,
        is_internal=is_internal,
    )
    db.add(message)
    await db.flush()
    return message


async def get_conversation_history(
    db: AsyncSession, conversation_id: int, limit: int = 10
) -> List[Message]:
    """Retrieve recent non-internal conversation history."""
    result = await db.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.is_internal.is_(False),
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()  # Chronological order
    return messages
