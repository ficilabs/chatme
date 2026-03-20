"""
Pydantic request/response schemas for the Chat and Session domains.

Keeping schemas here means:
- Any router can import them without circular deps.
- Frontend/client teams have a single source of truth.
- Easy to version (add schemas/v2/chat.py later).
"""
from __future__ import annotations
from pydantic import BaseModel, field_validator


# ── Chat ──────────────────────────────────────────────────────────────────────

class MessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty.")
        return v.strip()


class MessageResponse(BaseModel):
    response:   str
    session_id: str


class HistoryResponse(BaseModel):
    history:       list[dict]
    session_id:    str
    message_count: int


class ClearResponse(BaseModel):
    message:    str
    session_id: str


# ── Session ───────────────────────────────────────────────────────────────────

class SessionInfoResponse(BaseModel):
    session_id:    str
    message_count: int
    last_active:   float
    created_at:    float


class DeleteSessionResponse(BaseModel):
    message:    str
    session_id: str


# ── Health / Admin ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:   str
    version:  str
    redis_ok: bool


class StatsResponse(BaseModel):
    active_sessions: int
    store_type:      str
    redis_ok:        bool