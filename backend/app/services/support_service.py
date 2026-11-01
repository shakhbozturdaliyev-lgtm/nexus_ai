"""Support ticket management and operator escalation service."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.bot.session import save_message
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.conversation import Conversation, Message
from backend.app.models.customer import Customer
from backend.app.models.ticket import SupportTicket
from backend.app.models.user import User


class SupportService:
    """Service governing human operator escalation and support tickets."""

    async def escalate_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        reason: str,
        category: str = "general",
        priority: str = "medium",
    ) -> SupportTicket:
        """Transition conversation to 'awaiting_operator' and create support ticket."""
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = res.scalar_one_or_none()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found.")

        conversation.status = "awaiting_operator"

        ticket = SupportTicket(
            business_id=conversation.business_id,
            customer_id=conversation.customer_id,
            conversation_id=conversation.id,
            category=category,
            priority=priority,
            status="open",
        )
        db.add(ticket)

        # Log system handoff message
        await save_message(
            db,
            conversation_id=conversation.id,
            sender_type="system",
            content=f"Conversation escalated to human support. Reason: {reason}",
            message_type="handoff",
        )
        await db.commit()
        logger.info(f"Escalated conversation {conversation_id} -> SupportTicket {ticket.id}")
        return ticket

    async def claim_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        operator_id: int,
    ) -> Conversation:
        """Assign conversation and ticket to operator and mark 'operator_active'."""
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        conv.status = "operator_active"
        conv.assigned_operator_id = operator_id

        # Also assign any open tickets for this conversation
        t_res = await db.execute(
            select(SupportTicket).where(
                SupportTicket.conversation_id == conversation_id,
                SupportTicket.status.in_(["open", "in_progress"]),
            )
        )
        tickets = t_res.scalars().all()
        for t in tickets:
            t.status = "in_progress"
            t.assigned_operator_id = operator_id

        await db.commit()
        logger.info(f"Operator ID {operator_id} claimed conversation {conversation_id}")
        return conv

    async def send_operator_reply(
        self,
        db: AsyncSession,
        conversation_id: int,
        operator_id: int,
        content: str,
        bot_application: Optional[Any] = None,
    ) -> Message:
        """Send operator reply to customer and forward to Telegram."""
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        # Persist message
        msg = await save_message(
            db,
            conversation_id=conversation_id,
            sender_type="operator",
            content=content,
            message_type="text",
            is_internal=False,
        )
        await db.commit()

        # Forward to customer Telegram chat if bot application and customer telegram ID exist
        if bot_application:
            c_res = await db.execute(select(Customer).where(Customer.id == conv.customer_id))
            customer = c_res.scalar_one_or_none()
            if customer and customer.telegram_user_id:
                try:
                    await bot_application.bot.send_message(
                        chat_id=customer.telegram_user_id,
                        text=f"👨‍💼 *Operator:*\n{content}",
                        parse_mode="Markdown",
                    )
                except Exception as e:
                    logger.error(f"Failed to forward operator reply to Telegram: {e}")

        return msg

    async def add_internal_note(
        self,
        db: AsyncSession,
        conversation_id: int,
        operator_id: int,
        note_content: str,
    ) -> Message:
        """Add an internal operator note that is invisible to customers."""
        msg = await save_message(
            db,
            conversation_id=conversation_id,
            sender_type="operator",
            content=note_content,
            message_type="note",
            is_internal=True,
        )
        await db.commit()
        logger.info(f"Operator {operator_id} added internal note to conversation {conversation_id}")
        return msg

    async def return_to_ai(
        self,
        db: AsyncSession,
        conversation_id: int,
        operator_id: int,
    ) -> Conversation:
        """Return conversation back to AI handling mode."""
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        conv.status = "ai_active"
        conv.assigned_operator_id = None

        await save_message(
            db,
            conversation_id=conversation_id,
            sender_type="system",
            content="Conversation returned to AI handling mode.",
            message_type="handoff",
        )
        await db.commit()
        logger.info(f"Conversation {conversation_id} returned to AI mode by operator {operator_id}")
        return conv

    async def resolve_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        operator_id: int,
        resolution_notes: Optional[str] = None,
    ) -> Conversation:
        """Close conversation and resolve associated support tickets."""
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        now = datetime.now(timezone.utc)
        conv.status = "closed"
        conv.closed_at = now

        # Resolve tickets
        t_res = await db.execute(
            select(SupportTicket).where(SupportTicket.conversation_id == conversation_id)
        )
        tickets = t_res.scalars().all()
        for t in tickets:
            t.status = "resolved"
            t.resolved_at = now

        if resolution_notes:
            await save_message(
                db,
                conversation_id=conversation_id,
                sender_type="operator",
                content=f"Resolution note: {resolution_notes}",
                message_type="note",
                is_internal=True,
            )

        await db.commit()
        logger.info(f"Conversation {conversation_id} resolved and closed by operator {operator_id}")
        return conv


support_service = SupportService()
