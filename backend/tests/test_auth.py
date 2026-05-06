import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    user_data = {
        "username": "dupuser",
        "email": "dup1@example.com",
        "password": "pass123456",
    }
    await client.post("/api/auth/register", json=user_data)
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "dupuser",
            "email": "dup2@example.com",
            "password": "pass123456",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpass123",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "loginuser",
            "password": "loginpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "wrongpwuser",
            "email": "wrongpw@example.com",
            "password": "correctpass123",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "wrongpwuser",
            "password": "wrongpass123",
        },
    )
    assert response.status_code == 401
