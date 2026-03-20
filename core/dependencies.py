"""
FastAPI dependency providers.

Usage in any router:
    from core.dependencies import get_session_manager, get_chatbot, get_session

    @router.post("/chat")
    async def chat(
        sm: SessionManager = Depends(get_session_manager),
        bot: ChatBot       = Depends(get_chatbot),
    ): ...
"""
from __future__ import annotations

from typing import Optional
from fastapi import Depends, Header, HTTPException

from core.session_store import BaseSessionStore, SessionData


# ── Singletons (set once during app lifespan in main.py) ─────────────────────
# These are module-level holders — injected via Depends, never used directly.

_store: Optional[BaseSessionStore] = None
_bot   = None   # ChatBot — imported lazily to avoid circular imports


def set_store(store: BaseSessionStore) -> None:
    global _store
    _store = store


def set_bot(bot) -> None:
    global _bot
    _bot = bot


# ── Dependency: SessionManager ────────────────────────────────────────────────

def get_store() -> BaseSessionStore:
    if _store is None:
        raise RuntimeError("Session store not initialised.")
    return _store


# ── Dependency: ChatBot ───────────────────────────────────────────────────────

def get_chatbot():
    if _bot is None:
        raise RuntimeError("ChatBot not initialised.")
    return _bot


# ── Dependency: resolved session (requires X-Session-Id header) ───────────────

async def get_session(
    x_session_id: Optional[str] = Header(default=None),
    store: BaseSessionStore     = Depends(get_store),
) -> tuple[str, SessionData]:
    """
    Resolve an existing session from the X-Session-Id header.
    Raises HTTP 404 if missing or expired.
    Use this for endpoints that *require* an existing session.
    """
    if not x_session_id:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    data = await store.get(x_session_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    data.touch()
    await store.save(x_session_id, data)
    return x_session_id, data


# ── Dependency: optional session (creates new if missing) ────────────────────

async def get_or_create_session(
    x_session_id: Optional[str] = Header(default=None),
    store: BaseSessionStore     = Depends(get_store),
) -> tuple[str, SessionData]:
    """
    Return existing session or create a new one.
    Use this for the /chat endpoint where a new visitor is welcome.
    """
    import uuid
    if x_session_id:
        data = await store.get(x_session_id)
        if data:
            data.touch()
            await store.save(x_session_id, data)
            return x_session_id, data

    new_id = str(uuid.uuid4())
    data   = SessionData()
    await store.save(new_id, data)
    return new_id, data