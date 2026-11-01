"""Team members and operator user management API router."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Team Members"])


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "operator"  # owner, admin, operator, viewer


@router.get("")
async def list_team_members(
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List team members within tenant."""
    res = await db.execute(
        select(User)
        .where(User.business_id == current_user.business_id)
        .order_by(User.created_at.asc())
    )
    users = res.scalars().all()
    return {
        "count": len(users),
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team_member(
    req: UserCreateRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create or invite a new team member."""
    # Check if email is already taken
    res = await db.execute(select(User).where(User.email == req.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    new_user = User(
        business_id=current_user.business_id,
        email=req.email,
        password_hash=get_password_hash(req.password),
        full_name=req.full_name,
        role=req.role,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    return {"status": "created", "user_id": new_user.id}
