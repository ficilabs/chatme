"""
Singleton sentence-transformer embedding model.
Vector size: 384 — matches Qdrant collection 'chatme'.
"""
from __future__ import annotations
import logging
from sentence_transformers import SentenceTransformer
from core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(text: str) -> list[float]:
    """Return 384-dim vector for given text."""
    return get_model().encode(text, normalize_embeddings=True).tolist()