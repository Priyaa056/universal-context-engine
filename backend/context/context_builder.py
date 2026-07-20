from typing import List, Optional, Union

from .exceptions import ContextBuilderError
from .models import ContextChunk, ContextObject, ContextStatistics


class ContextBuilder:
    """Builds a structured context object from retrieved chunks."""

    def build(
        self,
        question: str,
        retrieved_chunks: Optional[List],
    ) -> ContextObject:
        self._validate_question_and_chunks(question, retrieved_chunks)

        chunks = retrieved_chunks or []
        total_chunks_received = len(chunks)

        # Normalise: accept ContextChunk objects, dicts with flat fields,
        # or dicts with a nested 'metadata' sub-dict.
        normalised: list[ContextChunk] = []
        for chunk in chunks:
            normalised.append(self._normalise(chunk))

        # Dedup by text content — when the same text appears in multiple
        # chunks keep only the instance with the highest score.
        score_by_text: dict[str, float] = {}
        chunk_by_text: dict[str, ContextChunk] = {}
        for chunk in normalised:
            key = chunk.text.strip()
            if key not in score_by_text or chunk.score > score_by_text[key]:
                score_by_text[key] = chunk.score
                chunk_by_text[key] = chunk

        ordered_chunks = sorted(
            chunk_by_text.values(),
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        duplicates_removed = total_chunks_received - len(ordered_chunks)

        statistics = ContextStatistics(
            total_chunks_received=total_chunks_received,
            duplicates_removed=duplicates_removed,
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

    def _normalise(self, chunk) -> ContextChunk:
        """Convert a ContextChunk or dict into a ContextChunk."""
        if isinstance(chunk, ContextChunk):
            return chunk

        if isinstance(chunk, dict):
            text = str(chunk.get("text") or chunk.get("content") or "").strip()
            score = float(chunk.get("score", 0.0) or 0.0)

            # Support both flat and nested metadata
            meta = chunk.get("metadata") or {}
            document_id = str(
                chunk.get("document_id") or meta.get("document_id") or ""
            )
            filename = str(
                chunk.get("filename")
                or chunk.get("document_name")
                or meta.get("filename")
                or meta.get("document_name")
                or "Unknown"
            )
            chunk_index = int(
                chunk.get("chunk_index")
                if chunk.get("chunk_index") is not None
                else meta.get("chunk_index", 0)
            )

            return ContextChunk(
                text=text,
                score=score,
                document_id=document_id,
                filename=filename,
                chunk_index=chunk_index,
            )

        raise ContextBuilderError(
            f"Unsupported chunk type: {type(chunk).__name__}. "
            "Expected ContextChunk or dict."
        )

    def _validate_question_and_chunks(
        self,
        question: str,
        retrieved_chunks: Optional[List],
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