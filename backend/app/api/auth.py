"""Authentication and user session API router."""

from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, verify_password
from backend.app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate administrative user and return JWT bearer token."""
    res = await db.execute(select(User).where(User.email == req.email))
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account has been disabled.",
        )

    claims = {
        "user_id": user.id,
        "business_id": user.business_id,
        "role": user.role,
        "full_name": user.full_name,
    }
    token = create_access_token(subject=user.email, claims=claims)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "business_id": user.business_id,
        },
    }


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Retrieve profile of the currently signed-in user."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "business_id": current_user.business_id,
    }
