"""
vector_store.py — ChromaDB Vector Store.

Thin, opinionated wrapper around ChromaDB's PersistentClient.
This is the ONLY module that imports chromadb directly.

What this module KNOWS about:
  - ChromaDB's Python API
  - The physical layout of the persisted data directory
  - Upsert / delete / query operations on a single collection

What this module DOES NOT KNOW about:
  - Embedding providers or models
  - Document upload, chunking, or extraction
  - FastAPI / HTTP
  - Application config (config is passed in at construction time)

Design Principles Applied:
  - Single Responsibility Principle (SRP): only manages vector CRUD
  - Dependency Inversion (DIP): callers depend on this class, not on chromadb directly
  - Singleton pattern: module-level getter to avoid re-initialising ChromaDB per request
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """A single result from a semantic similarity search."""
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    distance: float  # lower = more similar (L2 distance from ChromaDB)

    @property
    def score(self) -> float:
        """Similarity score in [0, 1] — 1 is most similar.

        Converts ChromaDB's L2 distance to a bounded similarity score.
        This is an approximation suitable for UI display.
        """
        return max(0.0, 1.0 - self.distance / 2.0)


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

class VectorStore:
    """
    Manages a ChromaDB collection for the Universal Context Engine.

    One collection (`uce_chunks`) stores all document chunk embeddings.
    Each chunk is stored with:
      - id:            "<document_id>_chunk_<chunk_index>"
      - embedding:     List[float] from the active EmbeddingProvider
      - document:      The chunk's raw text (used in results)
      - metadata:      {document_id, document_name, chunk_index}

    Usage:
        store = VectorStore(persist_dir="backend/data/chroma")
        store.upsert_chunks("doc-123", chunk_records, embeddings)
        results = store.query(query_embedding, n_results=5)
    """

    COLLECTION_NAME = "uce_chunks"

    def __init__(self, persist_dir: str) -> None:
        """
        Initialise the VectorStore and open the ChromaDB persistent client.

        Args:
            persist_dir: Path to the directory where ChromaDB writes its data.
                         Created automatically if it does not exist.
        """
        # Resolve relative paths from the backend root (parent of this file's parent)
        backend_root = Path(__file__).resolve().parent.parent
        resolved_dir = (
            Path(persist_dir)
            if Path(persist_dir).is_absolute()
            else backend_root / persist_dir
        )
        resolved_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "VectorStore initialising: persist_dir=%s",
            resolved_dir,
        )

        import chromadb  # deferred import — fail loudly on first use, not on import

        self._client = chromadb.PersistentClient(path=str(resolved_dir))
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "l2"},  # L2 distance (lower = more similar)
        )

        logger.info(
            "VectorStore ready: collection='%s', items=%d",
            self.COLLECTION_NAME,
            self._collection.count(),
        )

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def upsert_chunks(
        self,
        document_id: str,
        chunk_records: List[dict],
        embeddings: List[List[float]],
    ) -> int:
        """
        Insert or replace all chunks for a document.

        IDs are derived as "<document_id>_chunk_<chunk_index>" so that
        re-uploading the same document automatically overwrites the old vectors.

        Args:
            document_id:   The document's UUID.
            chunk_records: List of chunk dicts as stored in chunks.json.
                           Must contain: chunk_index, content, document_name.
            embeddings:    Parallel list of embedding vectors.

        Returns:
            Number of chunks upserted.

        Raises:
            ValueError: If lengths of chunk_records and embeddings differ.
        """
        if len(chunk_records) != len(embeddings):
            raise ValueError(
                f"Chunk/embedding count mismatch: "
                f"{len(chunk_records)} chunks vs {len(embeddings)} embeddings."
            )

        if not chunk_records:
            logger.warning("upsert_chunks() called with empty chunk list — skipping.")
            return 0

        ids = [
            f"{document_id}_chunk_{rec['chunk_index']}"
            for rec in chunk_records
        ]
        documents = [rec["content"] for rec in chunk_records]
        metadatas = [
            {
                "document_id": document_id,
                "document_name": rec.get("document_name", ""),
                "chunk_index": rec["chunk_index"],
            }
            for rec in chunk_records
        ]

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            "VectorStore.upsert_chunks(): document_id=%s, chunks=%d",
            document_id,
            len(ids),
        )
        return len(ids)

    def delete_document(self, document_id: str) -> None:
        """
        Remove all chunk vectors belonging to a document.

        Uses ChromaDB's `where` filter on the `document_id` metadata field.
        Safe to call even if the document has no vectors.

        Args:
            document_id: The document UUID whose chunks should be removed.
        """
        logger.info(
            "VectorStore.delete_document(): document_id=%s",
            document_id,
        )
        self._collection.delete(where={"document_id": document_id})

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[QueryResult]:
        """
        Perform a semantic similarity search.

        Args:
            query_embedding: Embedding vector of the search query.
            n_results:       Maximum number of results to return.
            document_ids:    Optional filter — restrict search to these document IDs.

        Returns:
            A list of QueryResult objects ordered by similarity (most similar first).
            Returns an empty list if the collection is empty.
        """
        count = self._collection.count()
        if count == 0:
            logger.warning("VectorStore.query(): collection is empty — returning [].")
            return []

        # ChromaDB raises if n_results > total items in collection
        capped_n = min(n_results, count)

        where = {"document_id": {"$in": document_ids}} if document_ids else None

        chroma_kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": capped_n,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            chroma_kwargs["where"] = where

        raw = self._collection.query(**chroma_kwargs)

        results: List[QueryResult] = []
        ids = raw.get("ids", [[]])[0]
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        for chunk_id, content, meta, distance in zip(ids, documents, metadatas, distances):
            results.append(
                QueryResult(
                    chunk_id=chunk_id,
                    document_id=meta.get("document_id", ""),
                    document_name=meta.get("document_name", ""),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    content=content,
                    distance=distance,
                )
            )

        logger.info(
            "VectorStore.query(): n_results=%d, returned=%d",
            n_results,
            len(results),
        )
        return results

    def collection_count(self) -> int:
        """Return the total number of vectors currently stored."""
        return self._collection.count()


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Return the module-level VectorStore singleton.

    Initialises it on the first call using application settings.
    Thread-safe for typical single-process FastAPI deployments.
    """
    global _vector_store
    if _vector_store is None:
        from config import get_settings
        settings = get_settings()
        _vector_store = VectorStore(persist_dir=settings.CHROMA_PERSIST_DIR)
    return _vector_store
