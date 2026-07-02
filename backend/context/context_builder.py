from typing import Any, Dict, List, Optional

from .exceptions import ContextBuilderError
from .models import ContextChunk, ContextObject, ContextStatistics
from .utils import deduplicate_chunks, normalize_chunk


class ContextBuilder:
    """Builds a structured context object from retrieved chunks without calling any LLM."""

    def __init__(self) -> None:
        self._validate_inputs = self._validate_question_and_chunks

    def build(self, question: str, retrieved_chunks: Optional[List[Dict[str, Any]]]) -> ContextObject:
        self._validate_question_and_chunks(question, retrieved_chunks)

        total_chunks_received = len(retrieved_chunks or [])

        normalized_chunks = [normalize_chunk(chunk) for chunk in (retrieved_chunks or [])]
        unique_chunks = deduplicate_chunks(normalized_chunks)

        ordered_chunks = sorted(
            unique_chunks,
            key=lambda chunk: chunk.get("score", 0.0),
            reverse=True,
        )

        context_chunks = [
            ContextChunk(
                text=chunk.get("text", ""),
                score=float(chunk.get("score", 0.0) or 0.0),
                document_id=str(chunk.get("document_id", "") or ""),
                filename=str(chunk.get("filename", "") or ""),
                chunk_index=int(chunk.get("chunk_index", 0) or 0),
            )
            for chunk in ordered_chunks
        ]

        statistics = ContextStatistics(
            total_chunks_received=total_chunks_received,
            duplicates_removed=total_chunks_received - len(context_chunks),
            final_chunks=len(context_chunks),
            total_context_characters=sum(len(chunk.text) for chunk in context_chunks),
        )

        return ContextObject(
            question=question.strip(),
            chunks=context_chunks,
            statistics=statistics,
        )

    def _validate_question_and_chunks(self, question: str, retrieved_chunks: Optional[List[Dict[str, Any]]]) -> None:
        if question is None:
            raise ContextBuilderError("Question cannot be None")

        if not isinstance(question, str):
            raise ContextBuilderError("Question must be a string")

        if not question.strip():
            raise ContextBuilderError("Question cannot be empty or whitespace-only")

        if retrieved_chunks is None:
            raise ContextBuilderError("Retrieved chunks cannot be None")

        if not isinstance(retrieved_chunks, list):
            raise ContextBuilderError("Retrieved chunks must be a list")
