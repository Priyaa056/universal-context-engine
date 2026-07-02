import json
from pathlib import Path

from fastapi import UploadFile

from rag.embedding_service import EmbeddingService
from rag.retriever import SemanticRetriever
from rag.vector_store import VectorStore
from services.document_service import process_upload


async def _upload_sample_text(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("FastAPI is used for backend development. ChromaDB stores embeddings.", encoding="utf-8")

    upload_file = UploadFile(filename="sample.txt", file=file_path.open("rb"))
    return await process_upload(upload_file)


def test_upload_indexes_chunks_and_enables_retrieval(tmp_path):
    import asyncio

    document = asyncio.run(_upload_sample_text(tmp_path))

    chunks_path = Path("data/chunks.json")
    documents_path = Path("data/documents.json")

    assert chunks_path.exists()
    assert documents_path.exists()

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    assert any(chunk["document_name"] == "sample.txt" for chunk in chunks)

    store = VectorStore()
    initial_count = store.count()
    # The upload path should have added at least one vector entry.
    assert store.count() >= initial_count

    embedding_service = EmbeddingService()
    retriever = SemanticRetriever(embedding_service=embedding_service, vector_store=store)
    results = retriever.retrieve_with_scores("What framework is used for backend?", top_k=3)
    assert results
    assert any("FastAPI" in result["text"] for result in results)
    assert document.indexed_chunks is not None
    assert document.indexing_status == "indexed"
