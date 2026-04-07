"""
Singleton Qdrant client.
"""
from __future__ import annotations
import logging
from qdrant_client import QdrantClient
from core.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

logger = logging.getLogger(__name__)
_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info("Qdrant connected — collection: %s", QDRANT_COLLECTION)
    return _client