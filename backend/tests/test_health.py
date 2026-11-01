"""Integration tests for health and readiness endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Verify /api/health returns 200 with service info."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "NEXUS AI"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_readiness_check(async_client: AsyncClient):
    """Verify /api/ready returns 200 and confirms database connectivity."""
    response = await async_client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["default_business_id"] == 1
