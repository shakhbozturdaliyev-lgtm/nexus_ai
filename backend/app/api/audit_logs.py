"""Security and Administrative Audit Logs API router."""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import require_role
from backend.app.core.database import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
):
    """View tamper-evident security audit logs."""
    res = await db.execute(
        select(AuditLog)
        .where(AuditLog.business_id == current_user.business_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    logs = res.scalars().all()
    return {
        "count": len(logs),
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "outcome": log.outcome,
                "ip_address": log.ip_address,
                "details": log.details,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
