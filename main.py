"""
ChatMe API — entry point.

This file only does three things:
  1. Create the FastAPI app.
  2. Register middleware and routers.
  3. Manage startup/shutdown (store + bot init).

Business logic → services/
Endpoints      → routers/
Pydantic models→ schemas/
Settings       → core/config.py
DI providers   → core/dependencies.py
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import (
    API_TITLE, API_DESCRIPTION, API_VERSION,
    ALLOWED_ORIGINS, UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN, SESSION_TTL_SECONDS,
)
from core.session_store import create_store
from core.dependencies import set_store, set_bot
from chatbot import ChatBot
from routers import chat, session, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    store = create_store(UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN, SESSION_TTL_SECONDS)
    bot   = ChatBot()
    set_store(store)
    set_bot(bot)
    logger.info("Startup — store=%s  redis_ok=%s", type(store).__name__, await store.ping())
    yield
    await store.close()
    logger.info("Shutdown complete.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(session.router)


# ── Dev entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)