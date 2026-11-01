"""AI Settings API router."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.ai_setting import AISetting
from backend.app.models.user import User

router = APIRouter(prefix="/api/ai-settings", tags=["AI Settings"])


class UpdateAISettingsRequest(BaseModel):
    model_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_output_tokens: Optional[int] = Field(default=None, ge=100, le=4096)
    context_window_turns: Optional[int] = Field(default=None, ge=2, le=30)
    tool_call_limit: Optional[int] = Field(default=None, ge=1, le=10)
    system_instructions: Optional[str] = None
    fallback_message: Optional[str] = None


@router.get("")
async def get_ai_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """View AI configuration for current tenant (secrets are strictly excluded)."""
    res = await db.execute(
        select(AISetting).where(AISetting.business_id == current_user.business_id)
    )
    setting = res.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="AI settings not found.")

    return {
        "business_id": setting.business_id,
        "model_name": setting.model_name,
        "is_enabled": setting.is_enabled,
        "temperature": setting.temperature,
        "max_output_tokens": setting.max_output_tokens,
        "context_window_turns": setting.context_window_turns,
        "tool_call_limit": setting.tool_call_limit,
        "system_instructions": setting.system_instructions,
        "escalation_rules": setting.escalation_rules,
        "fallback_message": setting.fallback_message,
        "updated_at": setting.updated_at.isoformat(),
    }


@router.put("")
async def update_ai_settings(
    req: UpdateAISettingsRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update AI parameters and guardrail thresholds."""
    res = await db.execute(
        select(AISetting).where(AISetting.business_id == current_user.business_id)
    )
    setting = res.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="AI settings not found.")

    if req.model_name is not None:
        setting.model_name = req.model_name
    if req.is_enabled is not None:
        setting.is_enabled = req.is_enabled
    if req.temperature is not None:
        setting.temperature = req.temperature
    if req.max_output_tokens is not None:
        setting.max_output_tokens = req.max_output_tokens
    if req.context_window_turns is not None:
        setting.context_window_turns = req.context_window_turns
    if req.tool_call_limit is not None:
        setting.tool_call_limit = req.tool_call_limit
    if req.system_instructions is not None:
        setting.system_instructions = req.system_instructions
    if req.fallback_message is not None:
        setting.fallback_message = req.fallback_message

    await db.commit()
    return {"status": "updated", "business_id": setting.business_id}
