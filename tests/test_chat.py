# tests/test_chat.py

import pytest


# ============================================
# CHAT TESTS
# ============================================

@pytest.mark.asyncio
async def test_ask_without_auth(client):
    """Test asking question without auth fails."""
    response = await client.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/ask",
        json={"question": "What is AI?"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ask_nonexistent_document(client, auth_headers):
    """Test asking question about non-existent document fails."""
    response = await client.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/ask",
        headers=auth_headers,
        json={"question": "What is AI?"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ask_empty_question(client, auth_headers):
    """Test asking empty question fails."""
    response = await client.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/ask",
        headers=auth_headers,
        json={"question": ""},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ask_short_question(client, auth_headers):
    """Test asking very short question fails."""
    response = await client.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/ask",
        headers=auth_headers,
        json={"question": "Hi"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_history_without_auth(client):
    """Test getting chat history without auth fails."""
    response = await client.get(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/history",
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_chat_history_nonexistent_document(client, auth_headers):
    """Test getting history for non-existent document fails."""
    response = await client.get(
        "/api/v1/chat/00000000-0000-0000-0000-000000000000/history",
        headers=auth_headers,
    )

    assert response.status_code == 404