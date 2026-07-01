"""
indexing_service.py — Document Indexing Service.

Orchestrates the embedding + vector storage pipeline for document chunks.
Called during document upload to index chunks into ChromaDB.

What this module KNOWS about:
  - EmbeddingService (for generating chunk embeddings)
  - VectorStore (for storing/deleting chunk embeddings)
  - The shape of chunk records from document_service

What this module DOES NOT KNOW about:
  - ChromaDB internals (delegated to VectorStore)
  - Specific embedding providers (delegated to EmbeddingService)
  - HTTP / FastAPI
  - Document text extraction or chunking logic

Design Principles Applied:
  - Single Responsibility Principle (SRP): only coordinates embedding + storage
  - Dependency Inversion (DIP): depends on abstractions, not concrete classes
  - Facade Pattern: hides the two-step embed+store complexity from callers
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional

from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result data class
# ---------------------------------------------------------------------------

@dataclass
class IndexResult:
    """Summary of a completed indexing operation."""
    document_id: str
    chunks_indexed: int
    elapsed_ms: float


# ---------------------------------------------------------------------------
# IndexingService
# ---------------------------------------------------------------------------

class IndexingService:
    """
    Orchestrates the embed + upsert pipeline for document indexing.

    Takes a list of chunk records (dicts from chunks.json), embeds their
    content using the EmbeddingService, and stores the resulting vectors
    in ChromaDB via the VectorStore.

    Usage:
        service = IndexingService(embedding_service, vector_store)
        result = service.index_document("doc-uuid", chunk_records)
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        """
        Args:
            embedding_service: Resolves text -> embedding vectors.
            vector_store:      Manages ChromaDB upsert / delete / query.
        """
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        logger.info("IndexingService initialised.")

    def index_document(
        self,
        document_id: str,
        chunk_records: List[dict],
    ) -> IndexResult:
        """
        Embed all chunks and upsert them into the vector store.

        Steps:
          1. Extract text content from each chunk record
          2. Batch-embed all texts in one provider call
          3. Filter out chunks that produced empty embeddings
          4. Upsert the valid (embedding, metadata) pairs to ChromaDB

        Args:
            document_id:   The document UUID (from document_service).
            chunk_records: List of chunk dicts. Expected keys:
                           chunk_index (int), content (str), document_name (str).

        Returns:
            IndexResult with document_id, chunks_indexed, elapsed_ms.

        Raises:
            RuntimeError: If embedding inference fails (propagated from EmbeddingService).
        """
        start = time.perf_counter()
        logger.info(
            "IndexingService.index_document(): document_id=%s, chunks=%d",
            document_id,
            len(chunk_records),
        )

        if not chunk_records:
            logger.warning("index_document() called with empty chunk list — skipping.")
            return IndexResult(document_id=document_id, chunks_indexed=0, elapsed_ms=0.0)

        texts = [rec["content"] for rec in chunk_records]
        embeddings = self._embedding_service.embed_documents(texts)

        # Filter out chunks with empty embeddings (e.g. whitespace-only content)
        valid_records = []
        valid_embeddings = []
        for rec, emb in zip(chunk_records, embeddings):
            if emb:
                valid_records.append(rec)
                valid_embeddings.append(emb)
            else:
                logger.warning(
                    "Chunk %d of document %s produced an empty embedding — skipping.",
                    rec.get("chunk_index", "?"),
                    document_id,
                )

        chunks_indexed = self._vector_store.upsert_chunks(
            document_id=document_id,
            chunk_records=valid_records,
            embeddings=valid_embeddings,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "IndexingService.index_document() complete: document_id=%s, indexed=%d, elapsed=%.1f ms",
            document_id,
            chunks_indexed,
            elapsed_ms,
        )

        return IndexResult(
            document_id=document_id,
            chunks_indexed=chunks_indexed,
            elapsed_ms=elapsed_ms,
        )

    def delete_document(self, document_id: str) -> None:
        """
        Remove all chunk vectors for a document from ChromaDB.

        Called when a document is re-uploaded (to replace stale vectors)
        or explicitly deleted.

        Args:
            document_id: The document UUID to remove vectors for.
        """
        logger.info(
            "IndexingService.delete_document(): document_id=%s",
            document_id,
        )
        self._vector_store.delete_document(document_id)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_indexing_service: Optional[IndexingService] = None


def get_indexing_service() -> IndexingService:
    """
    Return the module-level IndexingService singleton.

    Constructs it on the first call using the shared EmbeddingService
    and VectorStore singletons.
    """
    global _indexing_service
    if _indexing_service is None:
        from rag.embedding_service import EmbeddingService
        from rag.vector_store import get_vector_store

        _indexing_service = IndexingService(
            embedding_service=EmbeddingService(),
            vector_store=get_vector_store(),
        )
    return _indexing_service
