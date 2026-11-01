"""Business Settings and Profile API router."""

from typing import Annotated, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.business import Business
from backend.app.models.user import User

router = APIRouter(prefix="/api/business", tags=["Business Settings"])


class UpdateBusinessRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    contact_information: Optional[Dict[str, Any]] = None
    working_hours: Optional[Dict[str, Any]] = None


@router.get("")
async def get_business_details(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve business tenant settings."""
    res = await db.execute(select(Business).where(Business.id == current_user.business_id))
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found.")

    return {
        "id": b.id,
        "name": b.name,
        "description": b.description,
        "primary_language": b.primary_language,
        "supported_languages": b.supported_languages,
        "timezone": b.timezone,
        "contact_information": b.contact_information,
        "working_hours": b.working_hours,
        "active_status": b.active_status,
        "created_at": b.created_at.isoformat(),
        "updated_at": b.updated_at.isoformat(),
    }


@router.put("")
async def update_business(
    req: UpdateBusinessRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update business settings and working hours."""
    res = await db.execute(select(Business).where(Business.id == current_user.business_id))
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Business not found.")

    if req.name is not None:
        b.name = req.name
    if req.description is not None:
        b.description = req.description
    if req.timezone is not None:
        b.timezone = req.timezone
    if req.contact_information is not None:
        b.contact_information = req.contact_information
    if req.working_hours is not None:
        b.working_hours = req.working_hours

    await db.commit()
    return {"status": "updated", "business_id": b.id}
