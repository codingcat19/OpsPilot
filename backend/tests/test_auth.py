import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "securepass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": "securepass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "securepass123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "securepass123"},
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401
