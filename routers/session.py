"""Session router — GET /session, DELETE /session."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from core.dependencies import get_store, get_chatbot
from core.session_store import BaseSessionStore
from chatbot import ChatBot
from schemas.chat import SessionInfoResponse, DeleteSessionResponse
from services.chat_service import ChatService

router = APIRouter(tags=["Session"])


def _service(
    store: BaseSessionStore = Depends(get_store),
    bot:   ChatBot          = Depends(get_chatbot),
) -> ChatService:
    return ChatService(store, bot)


@router.get("/session", response_model=SessionInfoResponse)
async def session_info(
    x_session_id: Optional[str] = Header(default=None),
    svc: ChatService             = Depends(_service),
):
    """Return metadata about the current session."""
    try:
        data = await svc.get_session_info(x_session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    return SessionInfoResponse(
        session_id=x_session_id,
        message_count=data.message_count,
        last_active=data.last_active,
        created_at=data.created_at,
    )


@router.delete("/session", response_model=DeleteSessionResponse)
async def delete_session(
    x_session_id: Optional[str] = Header(default=None),
    svc: ChatService             = Depends(_service),
):
    """Permanently delete a session and free its storage."""
    try:
        await svc.delete_session(x_session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    return DeleteSessionResponse(
        message="Session deleted.",
        session_id=x_session_id,
    )