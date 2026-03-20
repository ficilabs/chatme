"""
ChatService — business logic layer.

Routers call this service; they never touch the store or bot directly.
This separation means you can:
  - Unit-test service logic without HTTP context.
  - Swap the LLM or store without touching any router.
  - Add cross-cutting concerns (analytics, rate-limit, RAG retrieval)
    in ONE place without touching endpoints.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from chatbot import ChatBot
from core.session_store import BaseSessionStore, SessionData

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, store: BaseSessionStore, bot: ChatBot) -> None:
        self.store = store
        self.bot   = bot

    # ── Session helpers ───────────────────────────────────────────────────────

    async def get_or_create_session(
        self, session_id: Optional[str]
    ) -> tuple[str, SessionData]:
        """Return existing session or create a new one."""
        if session_id:
            data = await self.store.get(session_id)
            if data:
                data.touch()
                await self.store.save(session_id, data)
                return session_id, data

        new_id = str(uuid.uuid4())
        data   = SessionData()
        await self.store.save(new_id, data)
        logger.info("Session created: %s", new_id)
        return new_id, data

    async def require_session(self, session_id: Optional[str]) -> tuple[str, SessionData]:
        """Return session or raise ValueError if not found / expired."""
        if not session_id:
            raise ValueError("No session_id provided.")
        data = await self.store.get(session_id)
        if data is None:
            raise ValueError(f"Session '{session_id}' not found or expired.")
        data.touch()
        await self.store.save(session_id, data)
        return session_id, data

    # ── Chat operations ───────────────────────────────────────────────────────

    async def send_message(
        self, message: str, session_id: Optional[str]
    ) -> tuple[str, str]:
        """
        Process one user message.
        Returns (reply, session_id).

        This is the place to add RAG retrieval, content filtering,
        usage logging, etc. — without touching the router.
        """
        sid, session_data = await self.get_or_create_session(session_id)

        # ── Future hook: inject RAG context into message here ──────────────
        # context = await retriever.fetch(message)
        # augmented = f"{context}\n\nUser: {message}"

        reply, updated_history = await self.bot.chat(message, session_data.history)

        session_data.history = updated_history
        await self.store.save(sid, session_data)

        logger.info("session=%s  msgs=%d", sid, session_data.message_count)
        return reply, sid

    async def get_history(self, session_id: str) -> tuple[list[dict], int]:
        """Return (history, message_count) for a session."""
        _, data = await self.require_session(session_id)
        return data.history, data.message_count

    async def clear_history(self, session_id: str) -> None:
        """Wipe history but keep session alive."""
        _, data = await self.require_session(session_id)
        data.history = []
        await self.store.save(session_id, data)

    async def get_session_info(self, session_id: str) -> SessionData:
        """Return full session metadata."""
        _, data = await self.require_session(session_id)
        return data

    async def delete_session(self, session_id: str) -> None:
        """Permanently remove a session."""
        await self.require_session(session_id)   # ensures it exists first
        await self.store.delete(session_id)
        logger.info("Session deleted: %s", session_id)

    # ── Admin ─────────────────────────────────────────────────────────────────

    async def active_session_count(self) -> int:
        return await self.store.active_count()

    async def is_store_healthy(self) -> bool:
        return await self.store.ping()

    def store_type(self) -> str:
        return type(self.store).__name__