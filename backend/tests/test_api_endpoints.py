"""Integration tests for administrative FastAPI REST endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_login_and_me(async_client: AsyncClient):
    """Test login flow and protected /me profile endpoint."""
    # Invalid login
    bad_res = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@demoelectronics.uz", "password": "WrongPassword!"},
    )
    assert bad_res.status_code == 401

    # Valid login
    login_res = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@demoelectronics.uz", "password": "AdminPass123!"},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    token = login_data["access_token"]
    assert token is not None

    # Test /me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await async_client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "admin@demoelectronics.uz"
    assert me_data["role"] == "owner"


@pytest.mark.asyncio
async def test_products_api(async_client: AsyncClient):
    """Test product listing and product creation."""
    # Obtain auth token
    login_res = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@demoelectronics.uz", "password": "AdminPass123!"},
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # List products
    list_res = await async_client.get("/api/products", headers=headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["count"] >= 3
    product_names = [p["name"] for p in data["items"]]
    assert "Samsung Galaxy A16" in product_names

    # Create new product
    new_prod = {
        "name": "Anker 20W Fast Charger",
        "brand": "Anker",
        "description": "USB-C Power Delivery 20W Compact Wall Charger",
        "variants": [
            {
                "sku": "ANK-20W-WHT",
                "color": "White",
                "price": 180000.0,
                "stock_quantity": 40,
            }
        ],
    }
    create_res = await async_client.post("/api/products", json=new_prod, headers=headers)
    assert create_res.status_code == 201
    assert "product_id" in create_res.json()


@pytest.mark.asyncio
async def test_ai_settings_api(async_client: AsyncClient):
    """Test viewing and updating AI configuration (ensuring no secret leakage)."""
    login_res = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@demoelectronics.uz", "password": "AdminPass123!"},
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = await async_client.get("/api/ai-settings", headers=headers)
    assert res.status_code == 200
    settings_data = res.json()
    assert settings_data["model_name"] == "gemini-2.5-flash"
    assert "api_key" not in settings_data  # Confidential secrets never exposed!

    # Update temperature
    update_res = await async_client.put(
        "/api/ai-settings", json={"temperature": 0.3}, headers=headers
    )
    assert update_res.status_code == 200


@pytest.mark.asyncio
async def test_analytics_api(async_client: AsyncClient):
    """Test overview metrics calculation."""
    login_res = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@demoelectronics.uz", "password": "AdminPass123!"},
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = await async_client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    metrics = res.json()
    assert "total_conversations" in metrics
    assert "active_conversations" in metrics
    assert "resolution_rate_percent" in metrics
    assert "estimated_ai_cost_usd" in metrics
