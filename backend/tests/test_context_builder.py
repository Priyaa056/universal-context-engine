import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from context.context_builder import ContextBuilder
from context.exceptions import ContextBuilderError


def make_chunk(text, score, document_id="doc-1", filename="file.txt", chunk_index=0):
    return {
        "text": text,
        "score": score,
        "metadata": {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": chunk_index,
        },
    }


def test_empty_input_returns_empty_context():
    builder = ContextBuilder()

    context = builder.build("What is this?", [])

    assert context.question == "What is this?"
    assert context.chunks == []
    assert context.statistics.total_chunks_received == 0
    assert context.statistics.duplicates_removed == 0
    assert context.statistics.final_chunks == 0
    assert context.statistics.total_context_characters == 0


def test_duplicate_removal_and_sorting():
    builder = ContextBuilder()
    chunks = [
        make_chunk("Alpha chunk", 0.2, document_id="doc-1", filename="a.txt", chunk_index=1),
        make_chunk("Alpha chunk", 0.9, document_id="doc-1", filename="a.txt", chunk_index=2),
        make_chunk("Beta chunk", 0.8, document_id="doc-2", filename="b.txt", chunk_index=3),
    ]

    context = builder.build("Question", chunks)

    assert len(context.chunks) == 2
    assert context.chunks[0].text == "Alpha chunk"
    assert context.chunks[0].score == 0.9
    assert context.chunks[1].text == "Beta chunk"
    assert context.chunks[1].score == 0.8
    assert context.statistics.duplicates_removed == 1
    assert context.statistics.final_chunks == 2
    assert context.statistics.total_chunks_received == 3


def test_metadata_is_preserved_from_retrieved_chunks():
    builder = ContextBuilder()
    chunk = make_chunk("Gamma chunk", 0.65, document_id="doc-3", filename="gamma.txt", chunk_index=7)

    context = builder.build("Question", [chunk])

    assert len(context.chunks) == 1
    chunk_context = context.chunks[0]
    assert chunk_context.document_id == "doc-3"
    assert chunk_context.filename == "gamma.txt"
    assert chunk_context.chunk_index == 7
    assert chunk_context.score == 0.65


def test_statistics_count_total_context_characters():
    builder = ContextBuilder()
    chunks = [
        make_chunk("One", 0.5),
        make_chunk("Two", 0.3),
    ]

    context = builder.build("Q", chunks)

    assert context.statistics.total_context_characters == 6


def test_supports_flat_metadata_fields_in_chunk_payloads():
    builder = ContextBuilder()
    chunks = [
        {
            "text": "FastAPI is used for backend development.",
            "score": 0.91,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 1,
        },
        {
            "text": "Next.js is used for frontend development.",
            "score": 0.88,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 3,
        },
    ]

    context = builder.build("Which framework is used for backend development?", chunks)

    assert len(context.chunks) == 2
    assert context.chunks[0].document_id == "doc1"
    assert context.chunks[0].filename == "project.pdf"
    assert context.chunks[0].chunk_index == 1
    assert context.chunks[0].score == 0.91


def test_invalid_inputs_raise_context_builder_error():
    builder = ContextBuilder()

    with pytest.raises(ContextBuilderError):
        builder.build("", [])

    with pytest.raises(ContextBuilderError):
        builder.build(None, [])

    with pytest.raises(ContextBuilderError):
        builder.build("Question", None)
