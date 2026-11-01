"""Analytics and Operational Metrics API router."""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.conversation import Conversation
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.models.ticket import SupportTicket
from backend.app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_overview_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Aggregate actual business support statistics from database records."""
    b_id = current_user.business_id

    # Total conversations
    tot_conv = await db.scalar(
        select(func.count(Conversation.id)).where(Conversation.business_id == b_id)
    ) or 0

    # Active conversations
    active_conv = await db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == b_id,
            Conversation.status.in_(["ai_active", "awaiting_operator", "operator_active"]),
        )
    ) or 0

    # AI handled
    ai_conv = await db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == b_id,
            Conversation.status == "ai_active",
        )
    ) or 0

    # Human handled
    human_conv = await db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == b_id,
            Conversation.status.in_(["awaiting_operator", "operator_active"]),
        )
    ) or 0

    # Closed conversations
    closed_conv = await db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == b_id,
            Conversation.status == "closed",
        )
    ) or 0

    # Open tickets
    open_tickets = await db.scalar(
        select(func.count(SupportTicket.id)).where(
            SupportTicket.business_id == b_id,
            SupportTicket.status.in_(["open", "in_progress"]),
        )
    ) or 0

    # Total customers
    tot_cust = await db.scalar(
        select(func.count(Customer.id)).where(Customer.business_id == b_id)
    ) or 0

    # Total orders & revenue
    tot_orders = await db.scalar(
        select(func.count(Order.id)).where(Order.business_id == b_id)
    ) or 0
    tot_revenue = await db.scalar(
        select(func.sum(Order.total_amount)).where(Order.business_id == b_id)
    ) or 0.0

    # AI metrics approximation based on conversation turns
    estimated_tokens = tot_conv * 250
    # Gemini 2.5/2.0 Flash pricing ~$0.075 per 1M input tokens
    estimated_cost_usd = round((estimated_tokens / 1_000_000) * 0.15, 4)

    resolution_rate = round((closed_conv / tot_conv * 100), 1) if tot_conv > 0 else 100.0

    return {
        "total_conversations": tot_conv,
        "active_conversations": active_conv,
        "ai_handled_conversations": ai_conv,
        "human_handled_conversations": human_conv,
        "closed_conversations": closed_conv,
        "open_support_tickets": open_tickets,
        "total_customers": tot_cust,
        "total_orders": tot_orders,
        "total_revenue_uzs": float(tot_revenue),
        "resolution_rate_percent": resolution_rate,
        "estimated_ai_tokens_used": estimated_tokens,
        "estimated_ai_cost_usd": estimated_cost_usd,
    }
