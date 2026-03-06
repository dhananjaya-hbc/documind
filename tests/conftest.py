# tests/conftest.py

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.main import app
from app.database import Base, get_db
from app.config import get_settings

settings = get_settings()


# ============================================
# Test Database Setup
# ============================================

# Use a separate test database
TEST_DATABASE_URL = settings.DATABASE_URL

test_engine = create_async_engine(TEST_DATABASE_URL)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


# ============================================
# Fixtures
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    """Register a test user and return credentials."""
    user_data = {
        "email": f"test_{asyncio.get_event_loop().time()}@test.com",
        "username": f"testuser_{int(asyncio.get_event_loop().time())}",
        "password": "testpassword123",
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "username": user_data["username"],
        "user": response.json() if response.status_code == 201 else None,
    }


@pytest_asyncio.fixture
async def auth_token(client, registered_user):
    """Get JWT token for authenticated requests."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    token = response.json()["access_token"]
    return token


@pytest_asyncio.fixture
async def auth_headers(auth_token):
    """Get authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}