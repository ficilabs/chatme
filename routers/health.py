"""Health router — GET /, GET /stats."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from core.config import API_VERSION
from core.dependencies import get_store, get_chatbot
from core.session_store import BaseSessionStore
from chatbot import ChatBot
from schemas.chat import HealthResponse, StatsResponse
from services.chat_service import ChatService

router = APIRouter(tags=["Health"])


def _service(
    store: BaseSessionStore = Depends(get_store),
    bot:   ChatBot          = Depends(get_chatbot),
) -> ChatService:
    return ChatService(store, bot)


@router.get("/", response_model=HealthResponse)
async def health_check(svc: ChatService = Depends(_service)):
    """Liveness + readiness probe."""
    return HealthResponse(
        status="ok",
        version=API_VERSION,
        redis_ok=await svc.is_store_healthy(),
    )


@router.get("/stats", response_model=StatsResponse)
async def stats(svc: ChatService = Depends(_service)):
    """Runtime statistics — active sessions, store type, Redis status."""
    return StatsResponse(
        active_sessions=await svc.active_session_count(),
        store_type=svc.store_type(),
        redis_ok=await svc.is_store_healthy(),
    )