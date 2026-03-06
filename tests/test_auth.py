# tests/test_auth.py

import pytest
import pytest_asyncio


# ============================================
# REGISTER TESTS
# ============================================

@pytest.mark.asyncio
async def test_register_success(client):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert data["is_active"] is True
    assert "id" in data
    # Password should NOT be in response
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Test registration with existing email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "password123",
    }

    # First registration
    await client.post("/api/v1/auth/register", json=user_data)

    # Second registration with same email
    user_data["username"] = "user2"
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test registration with invalid email fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    """Test registration with short password fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_username(client):
    """Test registration with short username fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "username": "ab",
            "password": "password123",
        },
    )

    assert response.status_code == 422


# ============================================
# LOGIN TESTS
# ============================================

@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    """Test successful login returns token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    """Test login with wrong password fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    """Test login with non-existent email fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401


# ============================================
# PROTECTED ROUTE TESTS
# ============================================

@pytest.mark.asyncio
async def test_get_me_with_token(client, auth_headers):
    """Test /me endpoint with valid token."""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_me_without_token(client):
    """Test /me endpoint without token fails."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_with_fake_token(client):
    """Test /me endpoint with fake token fails."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer fake-token-12345"},
    )

    assert response.status_code == 401


# ============================================
# HEALTH CHECK
# ============================================

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "DocuMind"