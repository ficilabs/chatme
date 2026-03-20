"""
Upstash Redis session store with transparent in-memory fallback.

Each session is stored as a JSON blob:
    key:   chatme:session:<session_id>
    value: {"history": [...], "created_at": float, "last_active": float}

TTL is managed via Redis EXPIRE — no manual purge loops needed.

The upstash-redis SDK is synchronous (HTTP REST), so every call is
offloaded via run_in_executor() to keep FastAPI's event loop free.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from upstash_redis import Redis as UpstashRedis
    _UPSTASH_AVAILABLE = True
except ImportError:
    _UPSTASH_AVAILABLE = False
    logger.warning("upstash-redis not installed — falling back to in-memory store.")

_KEY_PREFIX = "chatme:session:"


# ── SessionData ───────────────────────────────────────────────────────────────

class SessionData:
    """Plain serialisable container for one session."""

    def __init__(
        self,
        history: Optional[list[dict]] = None,
        created_at: Optional[float] = None,
        last_active: Optional[float] = None,
    ) -> None:
        now = time.time()
        self.history:     list[dict] = history or []
        self.created_at:  float      = created_at  or now
        self.last_active: float      = last_active or now

    def to_dict(self) -> dict:
        return {
            "history":     self.history,
            "created_at":  self.created_at,
            "last_active": self.last_active,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SessionData":
        return cls(
            history=d.get("history", []),
            created_at=d.get("created_at"),
            last_active=d.get("last_active"),
        )

    def touch(self) -> None:
        self.last_active = time.time()

    @property
    def message_count(self) -> int:
        return len(self.history)


# ── Abstract base ─────────────────────────────────────────────────────────────

class BaseSessionStore:
    async def get(self, session_id: str) -> Optional[SessionData]: ...
    async def save(self, session_id: str, data: SessionData) -> None: ...
    async def delete(self, session_id: str) -> None: ...
    async def exists(self, session_id: str) -> bool: ...
    async def active_count(self) -> int: ...
    async def ping(self) -> bool: ...
    async def close(self) -> None: ...


# ── Upstash implementation ────────────────────────────────────────────────────

class UpstashSessionStore(BaseSessionStore):
    """HTTP-based Redis via Upstash SDK (sync wrapped in executor)."""

    def __init__(self, url: str, token: str, ttl: int) -> None:
        self._redis = UpstashRedis(url=url, token=token)
        self._ttl   = ttl
        logger.info("UpstashSessionStore ready (ttl=%ds)", ttl)

    def _key(self, sid: str) -> str:
        return f"{_KEY_PREFIX}{sid}"

    async def _run(self, fn):
        return await asyncio.get_event_loop().run_in_executor(None, fn)

    async def get(self, session_id: str) -> Optional[SessionData]:
        raw = await self._run(lambda: self._redis.get(self._key(session_id)))
        if raw is None:
            return None
        data = raw if isinstance(raw, dict) else json.loads(raw)
        return SessionData.from_dict(data)

    async def save(self, session_id: str, data: SessionData) -> None:
        key, payload, ttl = self._key(session_id), json.dumps(data.to_dict()), self._ttl
        await self._run(lambda: self._redis.set(key, payload, ex=ttl))

    async def delete(self, session_id: str) -> None:
        key = self._key(session_id)
        await self._run(lambda: self._redis.delete(key))

    async def exists(self, session_id: str) -> bool:
        key = self._key(session_id)
        return bool(await self._run(lambda: self._redis.exists(key)))

    async def active_count(self) -> int:
        try:
            keys = await self._run(lambda: self._redis.keys(f"{_KEY_PREFIX}*"))
            return len(keys)
        except Exception:
            return 0

    async def ping(self) -> bool:
        try:
            result = await self._run(lambda: self._redis.ping())
            return str(result).upper() == "PONG"
        except Exception as exc:
            logger.warning("Upstash ping failed: %s", exc)
            return False

    async def close(self) -> None:
        logger.info("UpstashSessionStore closed (HTTP — no-op).")


# ── In-memory fallback ────────────────────────────────────────────────────────

class InMemorySessionStore(BaseSessionStore):
    """Dev/test fallback — data lost on restart."""

    def __init__(self, ttl: int) -> None:
        self._store: dict[str, SessionData] = {}
        self._ttl = ttl
        logger.warning("InMemorySessionStore active — sessions will NOT survive restarts.")

    def _expired(self, d: SessionData) -> bool:
        return (time.time() - d.last_active) > self._ttl

    def _purge(self) -> None:
        for k in [k for k, v in self._store.items() if self._expired(v)]:
            del self._store[k]

    async def get(self, session_id: str) -> Optional[SessionData]:
        self._purge()
        d = self._store.get(session_id)
        return None if (d is None or self._expired(d)) else d

    async def save(self, session_id: str, data: SessionData) -> None:
        self._store[session_id] = data

    async def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    async def exists(self, session_id: str) -> bool:
        return (await self.get(session_id)) is not None

    async def active_count(self) -> int:
        self._purge()
        return len(self._store)

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        pass


# ── Factory ───────────────────────────────────────────────────────────────────

def create_store(url: Optional[str], token: Optional[str], ttl: int) -> BaseSessionStore:
    if url and token:
        if not _UPSTASH_AVAILABLE:
            logger.error("upstash-redis not installed. Run: pip install upstash-redis")
            return InMemorySessionStore(ttl)
        return UpstashSessionStore(url=url, token=token, ttl=ttl)
    return InMemorySessionStore(ttl)