"""Conversations and Operator Live Support API router."""

from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.conversation import Conversation, Message
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.models.ticket import SupportTicket
from backend.app.models.user import User
from backend.app.services.support_service import support_service

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


class ReplyRequest(BaseModel):
    content: str


class NoteRequest(BaseModel):
    content: str


class ResolveRequest(BaseModel):
    resolution_notes: Optional[str] = None


@router.get("")
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Optional[str] = Query(None, description="Filter by status: ai_active, awaiting_operator, operator_active, closed"),
    search: Optional[str] = Query(None, description="Search by customer display name or ID"),
    limit: int = 50,
    offset: int = 0,
):
    """List customer support conversations with tenancy filtering."""
    stmt = (
        select(Conversation, Customer)
        .join(Customer, Conversation.customer_id == Customer.id)
        .where(Conversation.business_id == current_user.business_id)
    )

    if status and status != "all":
        stmt = stmt.where(Conversation.status == status)

    if search:
        stmt = stmt.where(Customer.display_name.ilike(f"%{search}%"))

    stmt = stmt.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    rows = res.all()

    items = []
    for conv, cust in rows:
        # Get last message
        last_m_res = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = last_m_res.scalar_one_or_none()

        items.append({
            "id": conv.id,
            "status": conv.status,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "assigned_operator_id": conv.assigned_operator_id,
            "customer": {
                "id": cust.id,
                "display_name": cust.display_name,
                "telegram_user_id": cust.telegram_user_id,
                "preferred_language": cust.preferred_language,
            },
            "last_message": {
                "sender_type": last_msg.sender_type if last_msg else None,
                "content": last_msg.content if last_msg else None,
                "created_at": last_msg.created_at.isoformat() if last_msg else None,
            } if last_msg else None,
        })

    return {"count": len(items), "items": items}


@router.get("/{conversation_id}")
async def get_conversation_details(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve full conversation details, transcripts, customer profile, and tickets."""
    stmt = (
        select(Conversation, Customer)
        .join(Customer, Conversation.customer_id == Customer.id)
        .where(
            Conversation.id == conversation_id,
            Conversation.business_id == current_user.business_id,
        )
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conv, cust = row

    # Fetch messages
    m_res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
    )
    messages = m_res.scalars().all()

    # Fetch active support tickets
    t_res = await db.execute(
        select(SupportTicket)
        .where(SupportTicket.conversation_id == conv.id)
        .order_by(SupportTicket.created_at.desc())
    )
    tickets = t_res.scalars().all()

    # Fetch customer orders
    o_res = await db.execute(
        select(Order)
        .where(Order.customer_id == cust.id)
        .order_by(Order.created_at.desc())
    )
    orders = o_res.scalars().all()

    return {
        "id": conv.id,
        "status": conv.status,
        "assigned_operator_id": conv.assigned_operator_id,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "closed_at": conv.closed_at.isoformat() if conv.closed_at else None,
        "customer": {
            "id": cust.id,
            "display_name": cust.display_name,
            "telegram_user_id": cust.telegram_user_id,
            "preferred_language": cust.preferred_language,
            "created_at": cust.created_at.isoformat(),
        },
        "messages": [
            {
                "id": m.id,
                "sender_type": m.sender_type,
                "content": m.content,
                "message_type": m.message_type,
                "is_internal": m.is_internal,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
        "tickets": [
            {
                "id": t.id,
                "category": t.category,
                "priority": t.priority,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in tickets
        ],
        "orders": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "status": o.status,
                "total_amount": float(o.total_amount),
                "currency": o.currency,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ],
    }


@router.post("/{conversation_id}/claim")
async def claim_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Assign conversation to the current operator and lock out AI."""
    conv = await support_service.claim_conversation(
        db, conversation_id=conversation_id, operator_id=current_user.id
    )
    return {"status": "claimed", "conversation_id": conv.id, "new_status": conv.status}


@router.post("/{conversation_id}/reply")
async def send_reply(
    conversation_id: int,
    req: ReplyRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send operator message to customer and forward to Telegram."""
    msg = await support_service.send_operator_reply(
        db=db,
        conversation_id=conversation_id,
        operator_id=current_user.id,
        content=req.content,
    )
    return {"status": "sent", "message_id": msg.id}


@router.post("/{conversation_id}/note")
async def add_note(
    conversation_id: int,
    req: NoteRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add private internal operator note."""
    msg = await support_service.add_internal_note(
        db=db,
        conversation_id=conversation_id,
        operator_id=current_user.id,
        note_content=req.content,
    )
    return {"status": "saved", "note_id": msg.id}


@router.post("/{conversation_id}/return_to_ai")
async def return_to_ai(
    conversation_id: int,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return conversation to autonomous AI handling mode."""
    conv = await support_service.return_to_ai(
        db=db, conversation_id=conversation_id, operator_id=current_user.id
    )
    return {"status": "ai_active", "conversation_id": conv.id}


@router.post("/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: int,
    req: ResolveRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resolve and close conversation and tickets."""
    conv = await support_service.resolve_conversation(
        db=db,
        conversation_id=conversation_id,
        operator_id=current_user.id,
        resolution_notes=req.resolution_notes,
    )
    return {"status": "closed", "conversation_id": conv.id}
