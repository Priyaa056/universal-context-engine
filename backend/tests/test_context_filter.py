import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from context.context_filter import ContextFilter


def make_chunk(text, score, document_id="doc-1", filename="file.txt", chunk_index=0):
    return {
        "text": text,
        "score": score,
        "document_id": document_id,
        "filename": filename,
        "chunk_index": chunk_index,
    }


def test_empty_input_is_handled_safely():
    filter_service = ContextFilter()

    result = filter_service.filter([])

    assert result.chunks == []
    assert result.statistics.total_chunks_received == 0
    assert result.statistics.chunks_removed_by_score == 0
    assert result.statistics.chunks_removed_by_limit == 0
    assert result.statistics.final_chunks == 0
    assert result.statistics.total_context_characters == 0


def test_low_score_chunks_are_removed():
    filter_service = ContextFilter(minimum_score=0.5)
    chunks = [
        make_chunk("High relevance", 0.9),
        make_chunk("Low relevance", 0.4),
    ]

    result = filter_service.filter(chunks)

    assert len(result.chunks) == 1
    assert result.chunks[0].text == "High relevance"
    assert result.statistics.chunks_removed_by_score == 1
    assert result.statistics.final_chunks == 1


def test_max_chunks_is_respected():
    filter_service = ContextFilter(max_chunks=2)
    chunks = [
        make_chunk("One", 0.9),
        make_chunk("Two", 0.8),
        make_chunk("Three", 0.7),
    ]

    result = filter_service.filter(chunks)

    assert len(result.chunks) == 2
    assert [chunk.text for chunk in result.chunks] == ["One", "Two"]
    assert result.statistics.chunks_removed_by_limit == 1


def test_max_context_characters_is_respected():
    filter_service = ContextFilter(max_context_characters=20)
    chunks = [
        make_chunk("Alpha beta", 0.9),
        make_chunk("Gamma delta", 0.8),
    ]

    result = filter_service.filter(chunks)

    assert result.statistics.total_context_characters <= 20
    assert len(result.chunks) <= 2
    assert result.statistics.final_chunks <= 2


def test_metadata_is_preserved():
    filter_service = ContextFilter()
    chunk = make_chunk("Metadata chunk", 0.8, document_id="doc-42", filename="notes.txt", chunk_index=9)

    result = filter_service.filter([chunk])

    assert len(result.chunks) == 1
    filtered_chunk = result.chunks[0]
    assert filtered_chunk.document_id == "doc-42"
    assert filtered_chunk.filename == "notes.txt"
    assert filtered_chunk.chunk_index == 9
    assert filtered_chunk.score == 0.8


def test_statistics_are_correct_after_filtering():
    filter_service = ContextFilter(minimum_score=0.6, max_chunks=2, max_context_characters=15)
    chunks = [
        make_chunk("Keep me", 0.9),
        make_chunk("Too low", 0.4),
        make_chunk("Long text chunk", 0.8),
        make_chunk("Short", 0.7),
        make_chunk("Another", 0.6),
    ]

    result = filter_service.filter(chunks)

    assert result.statistics.total_chunks_received == 5
    assert result.statistics.chunks_removed_by_score == 1
    assert result.statistics.chunks_removed_by_limit == 2
    assert result.statistics.final_chunks == 2
    assert result.statistics.total_context_characters == 12
