"""Support Tickets API router."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.customer import Customer
from backend.app.models.ticket import SupportTicket
from backend.app.models.user import User

router = APIRouter(prefix="/api/tickets", tags=["Support Tickets"])


class UpdateTicketRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_operator_id: Optional[int] = None


@router.get("")
async def list_tickets(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Optional[str] = None,
):
    """List business support tickets."""
    stmt = (
        select(SupportTicket, Customer)
        .join(Customer, SupportTicket.customer_id == Customer.id)
        .where(SupportTicket.business_id == current_user.business_id)
        .order_by(SupportTicket.created_at.desc())
    )
    if status and status != "all":
        stmt = stmt.where(SupportTicket.status == status)

    res = await db.execute(stmt)
    rows = res.all()

    items = []
    for ticket, cust in rows:
        items.append({
            "id": ticket.id,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "conversation_id": ticket.conversation_id,
            "assigned_operator_id": ticket.assigned_operator_id,
            "created_at": ticket.created_at.isoformat(),
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            "customer": {
                "id": cust.id,
                "display_name": cust.display_name,
                "preferred_language": cust.preferred_language,
            },
        })

    return {"count": len(items), "items": items}


@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    req: UpdateTicketRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update ticket priority, status, or assignment."""
    res = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.business_id == current_user.business_id,
        )
    )
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    if req.status is not None:
        ticket.status = req.status
    if req.priority is not None:
        ticket.priority = req.priority
    if req.assigned_operator_id is not None:
        ticket.assigned_operator_id = req.assigned_operator_id

    await db.commit()
    return {"status": "updated", "ticket_id": ticket.id}
