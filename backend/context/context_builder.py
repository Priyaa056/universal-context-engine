from typing import List, Optional

from .exceptions import ContextBuilderError
from .models import ContextChunk, ContextObject, ContextStatistics


class ContextBuilder:
    """Builds a structured context object from retrieved chunks."""

    def build(
        self,
        question: str,
        retrieved_chunks: Optional[List[ContextChunk]],
    ) -> ContextObject:
        self._validate_question_and_chunks(question, retrieved_chunks)

        chunks = retrieved_chunks or []
        total_chunks_received = len(chunks)

        unique_chunks: list[ContextChunk] = []
        seen_keys: set[tuple[str, int, str]] = set()

        for chunk in chunks:
            key = (
                chunk.document_id,
                chunk.chunk_index,
                chunk.text.strip(),
            )

            if key in seen_keys:
                continue

            seen_keys.add(key)
            unique_chunks.append(chunk)

        ordered_chunks = sorted(
            unique_chunks,
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        statistics = ContextStatistics(
            total_chunks_received=total_chunks_received,
            duplicates_removed=total_chunks_received - len(ordered_chunks),
            final_chunks=len(ordered_chunks),
            total_context_characters=sum(
                len(chunk.text) for chunk in ordered_chunks
            ),
        )

        return ContextObject(
            question=question.strip(),
            chunks=ordered_chunks,
            statistics=statistics,
        )

    def _validate_question_and_chunks(
        self,
        question: str,
        retrieved_chunks: Optional[List[ContextChunk]],
    ) -> None:
        if question is None:
            raise ContextBuilderError("Question cannot be None")

        if not isinstance(question, str):
            raise ContextBuilderError("Question must be a string")

        if not question.strip():
            raise ContextBuilderError(
                "Question cannot be empty or whitespace-only"
            )

        if retrieved_chunks is None:
            raise ContextBuilderError(
                "Retrieved chunks cannot be None"
            )

        if not isinstance(retrieved_chunks, list):
            raise ContextBuilderError(
                "Retrieved chunks must be a list"
            )

        if not all(
            isinstance(chunk, ContextChunk)
            for chunk in retrieved_chunks
        ):
            raise ContextBuilderError(
                "Every retrieved chunk must be a ContextChunk"
            )