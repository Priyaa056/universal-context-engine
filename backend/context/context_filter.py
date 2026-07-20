from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .exceptions import ContextBuilderError
from .models import ContextChunk


@dataclass(frozen=True)
class FilterStatistics:
    total_chunks_received: int
    chunks_removed_by_score: int
    chunks_removed_by_limit: int
    final_chunks: int
    total_context_characters: int


@dataclass(frozen=True)
class FilteredContext:
    chunks: List[ContextChunk]
    statistics: FilterStatistics


class ContextFilter:
    """Filters candidate chunks before they are turned into a final context object."""

    def __init__(self, minimum_score: float = 0.15, max_chunks: int = 5, max_context_characters: int = 4000) -> None:
        self.minimum_score = self._validate_config(minimum_score, max_chunks, max_context_characters)
        self.max_chunks = max_chunks
        self.max_context_characters = max_context_characters

    def filter(self, chunks: Optional[List[Dict[str, Any]]]) -> FilteredContext:
        if chunks is None:
            raise ContextBuilderError("Chunks cannot be None")

        if not isinstance(chunks, list):
            raise ContextBuilderError("Chunks must be a list")

        total_chunks_received = len(chunks)

        if total_chunks_received == 0:
            return FilteredContext(
                chunks=[],
                statistics=FilterStatistics(0, 0, 0, 0, 0),
            )

        scored_chunks = [
        chunk
        for chunk in chunks
        if self._is_chunk_eligible(chunk)
        ]
        chunks_removed_by_score = total_chunks_received - len(scored_chunks)

        # Normalise to ContextChunk for downstream processing
        ordered_chunks = sorted(
            [self._normalise(c) for c in scored_chunks],
            key=lambda chunk: chunk.score,
            reverse=True,
        )
        selected_chunks: List[ContextChunk] = []
        total_characters = 0
        chunks_removed_by_limit = 0

        for chunk in ordered_chunks:
            if len(selected_chunks) >= self.max_chunks:
                chunks_removed_by_limit += 1
                continue

            if total_characters + len(chunk.text) > self.max_context_characters:
                chunks_removed_by_limit += 1
                continue

            selected_chunks.append(chunk)
            total_characters += len(chunk.text)

        chunks_removed_by_limit += max(0, len(ordered_chunks) - len(selected_chunks) - chunks_removed_by_limit)

        return FilteredContext(
            chunks=selected_chunks,
            statistics=FilterStatistics(
                total_chunks_received=total_chunks_received,
                chunks_removed_by_score=chunks_removed_by_score,
                chunks_removed_by_limit=chunks_removed_by_limit,
                final_chunks=len(selected_chunks),
                total_context_characters=total_characters,
            ),
        )

    def _normalise(self, chunk) -> ContextChunk:
        """Convert a ContextChunk or dict into a ContextChunk."""
        if isinstance(chunk, ContextChunk):
            return chunk

        meta = chunk.get("metadata") or {}
        return ContextChunk(
            text=str(chunk.get("text") or chunk.get("content") or "").strip(),
            score=float(chunk.get("score", 0.0) or 0.0),
            document_id=str(
                chunk.get("document_id") or meta.get("document_id") or ""
            ),
            filename=str(
                chunk.get("filename")
                or chunk.get("document_name")
                or meta.get("filename")
                or "Unknown"
            ),
            chunk_index=int(
                chunk.get("chunk_index")
                if chunk.get("chunk_index") is not None
                else meta.get("chunk_index", 0)
            ),
        )

    def _is_chunk_eligible(self, chunk) -> bool:
        """Return True if chunk meets the minimum score threshold.

        Accepts both ContextChunk objects and plain dicts.
        """
        if isinstance(chunk, ContextChunk):
            return chunk.score >= self.minimum_score

        if isinstance(chunk, dict):
            return float(chunk.get("score", 0.0) or 0.0) >= self.minimum_score

        return False

    def _validate_config(self, minimum_score: float, max_chunks: int, max_context_characters: int) -> float:
        if not isinstance(minimum_score, (int, float)):
            raise ContextBuilderError("minimum_score must be a number")

        if minimum_score < 0:
            raise ContextBuilderError("minimum_score cannot be negative")

        if not isinstance(max_chunks, int) or max_chunks <= 0:
            raise ContextBuilderError("max_chunks must be a positive integer")

        if not isinstance(max_context_characters, int) or max_context_characters <= 0:
            raise ContextBuilderError("max_context_characters must be a positive integer")

        return float(minimum_score)
