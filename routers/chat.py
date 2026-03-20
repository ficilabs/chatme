"""Chat router — /chat, /history, /clear."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from core.dependencies import get_store, get_chatbot
from core.session_store import BaseSessionStore
from chatbot import ChatBot
from schemas.chat import (
    MessageRequest, MessageResponse,
    HistoryResponse, ClearResponse,
)
from services.chat_service import ChatService

logger   = logging.getLogger(__name__)
router   = APIRouter(tags=["Chat"])


def _service(
    store: BaseSessionStore = Depends(get_store),
    bot:   ChatBot          = Depends(get_chatbot),
) -> ChatService:
    return ChatService(store, bot)


@router.post("/chat", response_model=MessageResponse)
async def chat(
    request: MessageRequest,
    x_session_id: Optional[str] = Header(default=None),
    svc: ChatService             = Depends(_service),
):
    """
    Send a message and receive a reply.

    - Pass `X-Session-Id` header to continue an existing conversation.
    - Omit it to auto-create a new session; save the returned `session_id`.
    """
    try:
        reply, session_id = await svc.send_message(request.message, x_session_id)
    except Exception as exc:
        logger.exception("LLM error")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    return MessageResponse(response=reply, session_id=session_id)


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    x_session_id: Optional[str] = Header(default=None),
    svc: ChatService             = Depends(_service),
):
    """Retrieve the full conversation history for a session."""
    try:
        history, count = await svc.get_history(x_session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    return HistoryResponse(
        history=history,
        session_id=x_session_id,
        message_count=count,
    )


@router.post("/clear", response_model=ClearResponse)
async def clear_history(
    x_session_id: Optional[str] = Header(default=None),
    svc: ChatService             = Depends(_service),
):
    """Clear conversation history while keeping the session alive."""
    try:
        await svc.clear_history(x_session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    return ClearResponse(
        message="Conversation history cleared.",
        session_id=x_session_id,
    )