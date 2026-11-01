"""Shared pytest configuration and test fixtures."""

import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Override database URL to a dedicated test database before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_nexus_ai.db"
os.environ["APP_ENV"] = "testing"

from backend.app.core.database import Base, get_db
from backend.app.database.seed import seed_data
from backend.app.main import app

test_engine = create_async_engine(
    "sqlite+aiosqlite:///./test_nexus_ai.db",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create test tables and seed data once for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Run seed
    await seed_data()

    yield

    # Clean up test database after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists("./test_nexus_ai.db"):
        try:
            os.remove("./test_nexus_ai.db")
        except Exception:
            pass


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide an isolated database session for a test."""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """HTTP client configured for testing FastAPI endpoints."""
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
