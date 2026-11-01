"""Database engine, async session factory, and base ORM model."""

from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Configure engine arguments based on driver
engine_kwargs = {"echo": False, "future": True}

# SQLite-specific connection arguments
if "sqlite" in settings.database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

async_engine = create_async_engine(settings.database_url, **engine_kwargs)

# Enable Foreign Key constraints and WAL mode on SQLite connections
if "sqlite" in settings.database_url:
    @event.listens_for(async_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy entities."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an isolated async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rolled back due to error: {e}")
            raise
