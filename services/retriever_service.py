"""
RAG retriever service.

Payload structure in Qdrant 'chatme' collection:
{
    "id": 1,
    "type": "base",
    "category": "career",
    "content": "IT Trainer di ...",
    "metadata": {
        "role": "IT Trainer",
        "organization": "...",
        "start_date": "2025-04",
        "end_date": "2025-06",
        "role_type": "teaching"
    }
}
"""
from __future__ import annotations
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import QueryRequest
from core.config import QDRANT_COLLECTION, RETRIEVER_TOP_K
from core.embeddings import embed

logger = logging.getLogger(__name__)

SCORE_THRESHOLD = 0.30


class RetrieverService:
    def __init__(self, client: QdrantClient) -> None:
        self.client = client
        self.collection = QDRANT_COLLECTION

    async def retrieve(self, query: str, top_k: int = RETRIEVER_TOP_K) -> str:
        query_vector = embed(query)

        # qdrant-client >= 1.7: gunakan query_points()
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            score_threshold=SCORE_THRESHOLD,
            with_payload=True,
        ).points                          # ← .points untuk ambil list-nya

        if not results:
            logger.debug("No relevant chunks found for: %s", query[:60])
            return ""

        chunks: list[str] = []
        for hit in results:
            p = hit.payload or {}
            meta = p.get("metadata") or {}
            category = p.get("category", "info").upper()
            content  = p.get("content", "")

            lines = [f"[{category}] {content}"]

            if meta.get("role"):
                lines.append(f"  Role       : {meta['role']}")
            if meta.get("organization"):
                lines.append(f"  Organisasi : {meta['organization']}")
            if meta.get("start_date"):
                end = meta.get("end_date", "sekarang")
                lines.append(f"  Periode    : {meta['start_date']} – {end}")
            if meta.get("role_type"):
                lines.append(f"  Tipe       : {meta['role_type']}")

            for key in ("tech_stack", "description", "institution",
                        "degree", "field", "gpa", "link"):
                val = meta.get(key)
                if val:
                    lines.append(f"  {key.capitalize():10}: {val}")

            chunks.append("\n".join(lines))
            logger.debug("Hit score=%.3f  category=%s  content=%s",
                         hit.score, category, content[:50])

        context = "\n\n".join(chunks)
        logger.info("RAG: %d chunks retrieved for query '%s'",
                    len(chunks), query[:50])
        return context