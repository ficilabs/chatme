"""
Unit tests for ChatService and store layer.
Run: pytest tests/ -v
"""
import pytest
import time
from unittest.mock import AsyncMock, MagicMock

from core.session_store import SessionData, InMemorySessionStore
from services.chat_service import ChatService


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_bot(reply: str = "Hello from FICI!"):
    bot = MagicMock()
    bot.chat = AsyncMock(return_value=(reply, [
        {"role": "user",      "content": "hi"},
        {"role": "assistant", "content": reply},
    ]))
    return bot


def make_service(reply: str = "Hello from FICI!") -> ChatService:
    store = InMemorySessionStore(ttl=3600)
    bot   = make_bot(reply)
    return ChatService(store, bot)


# ── send_message ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_message_creates_session():
    svc = make_service()
    reply, sid = await svc.send_message("hi", None)
    assert reply == "Hello from FICI!"
    assert sid is not None


@pytest.mark.asyncio
async def test_send_message_reuses_session():
    svc = make_service()
    _, sid1 = await svc.send_message("hi", None)
    _, sid2 = await svc.send_message("hello again", sid1)
    assert sid1 == sid2


@pytest.mark.asyncio
async def test_send_message_saves_history():
    store = InMemorySessionStore(ttl=3600)
    bot   = make_bot("ok")
    svc   = ChatService(store, bot)
    _, sid = await svc.send_message("test", None)
    data = await store.get(sid)
    assert data is not None
    assert len(data.history) == 2


# ── get_history ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_history_returns_correct_data():
    svc = make_service()
    _, sid = await svc.send_message("hi", None)
    history, count = await svc.get_history(sid)
    assert count == 2
    assert history[0]["role"] == "user"


@pytest.mark.asyncio
async def test_get_history_raises_for_missing_session():
    svc = make_service()
    with pytest.raises(ValueError):
        await svc.get_history("nonexistent-session-id")


# ── clear_history ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_history():
    svc = make_service()
    _, sid = await svc.send_message("hi", None)
    await svc.clear_history(sid)
    history, count = await svc.get_history(sid)
    assert count == 0
    assert history == []


# ── delete_session ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_session():
    svc = make_service()
    _, sid = await svc.send_message("hi", None)
    await svc.delete_session(sid)
    with pytest.raises(ValueError):
        await svc.get_history(sid)


@pytest.mark.asyncio
async def test_delete_nonexistent_raises():
    svc = make_service()
    with pytest.raises(ValueError):
        await svc.delete_session("ghost-session")


# ── InMemorySessionStore ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_store_ttl_expiry():
    store = InMemorySessionStore(ttl=1)
    data  = SessionData()
    data.last_active = time.time() - 2     # simulate expired
    await store.save("old", data)
    assert await store.get("old") is None


@pytest.mark.asyncio
async def test_store_active_count():
    store = InMemorySessionStore(ttl=3600)
    await store.save("a", SessionData())
    await store.save("b", SessionData())
    assert await store.active_count() == 2
    await store.delete("a")
    assert await store.active_count() == 1


# ── API smoke tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_health():
    from httpx import AsyncClient, ASGITransport
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_api_empty_message_rejected():
    from httpx import AsyncClient, ASGITransport
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/chat", json={"message": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_api_history_without_session_returns_404():
    from httpx import AsyncClient, ASGITransport
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/history")
    assert resp.status_code == 404