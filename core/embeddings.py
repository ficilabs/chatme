"""
Singleton sentence-transformer embedding model.
Vector size: 384 — matches Qdrant collection 'chatme'.
"""
from __future__ import annotations
import logging
from fastembed import TextEmbedding
from core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        logger.info("Loading FastEmbed model: %s", EMBEDDING_MODEL)
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def embed(text: str) -> list[float]:
    """Return 384-dim vector — compatible dengan Qdrant collection chatme."""
    model = get_model()
    vectors = list(model.embed([text]))   # FastEmbed returns generator
    return vectors[0].tolist()