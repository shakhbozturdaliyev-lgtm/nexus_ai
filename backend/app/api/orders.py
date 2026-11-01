"""Orders management API router."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.customer import Customer
from backend.app.models.order import Order, OrderItem, OrderStatusHistory
from backend.app.models.user import User

router = APIRouter(prefix="/api/orders", tags=["Orders"])


class UpdateOrderStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None


@router.get("")
async def list_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Optional[str] = None,
):
    """List business customer orders."""
    stmt = (
        select(Order, Customer)
        .join(Customer, Order.customer_id == Customer.id)
        .where(Order.business_id == current_user.business_id)
        .order_by(Order.created_at.desc())
    )
    if status and status != "all":
        stmt = stmt.where(Order.status == status)

    res = await db.execute(stmt)
    rows = res.all()

    orders_list = []
    for order, customer in rows:
        orders_list.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "currency": order.currency,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at.isoformat(),
            "customer": {
                "id": customer.id,
                "display_name": customer.display_name,
                "telegram_user_id": customer.telegram_user_id,
            },
        })

    return {"count": len(orders_list), "items": orders_list}


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    req: UpdateOrderStatusRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin", "operator"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update order fulfillment status and log history."""
    res = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.business_id == current_user.business_id,
        )
    )
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    order.status = req.status
    history_entry = OrderStatusHistory(
        order_id=order.id,
        status=req.status,
        notes=req.notes,
    )
    db.add(history_entry)
    await db.commit()
    return {"status": "updated", "order_id": order.id, "new_status": order.status}
