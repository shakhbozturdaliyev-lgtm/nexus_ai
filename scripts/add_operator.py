"""Add a new support operator to NEXUS AI."""

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.user import User


async def add_operator():
    email = "shakhbozturdaliyev@gmail.com"
    full_name = "Shakhboz Turdaliyev"
    role = "operator"
    password = "Operator2026!"
    business_id = 1

    async with AsyncSessionLocal() as session:
        # Check if already exists
        result = await session.execute(
            select(User).where(User.email == email, User.business_id == business_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.role = role
            existing.full_name = full_name
            existing.password_hash = get_password_hash(password)
            existing.is_active = True
            await session.commit()
            print(f"Updated existing user: {email} to role: {role}")
        else:
            user = User(
                business_id=business_id,
                email=email,
                full_name=full_name,
                password_hash=get_password_hash(password),
                role=role,
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Successfully created operator ID {user.id}: {email}")


if __name__ == "__main__":
    asyncio.run(add_operator())
