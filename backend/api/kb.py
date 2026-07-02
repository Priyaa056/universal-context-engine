import logging
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from config import get_settings
from models.schemas import (
    DocumentsListResponse,
    ErrorResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    UploadSuccessResponse,
)
from rag.embedding_service import EmbeddingService
from rag.retriever import SemanticRetriever
from rag.vector_store import VectorStore
from services.document_service import DocumentProcessingError, list_documents, process_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])


@lru_cache
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(
        provider_name=settings.EMBEDDING_PROVIDER,
        model_name=settings.EMBEDDING_MODEL_NAME,
    )


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    return VectorStore(persist_directory=settings.CHROMA_PERSIST_DIR)


def get_retriever(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStore = Depends(get_vector_store),
) -> SemanticRetriever:
    return SemanticRetriever(embedding_service=embedding_service, vector_store=vector_store)


@router.post(
    "/upload",
    response_model=UploadSuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_document(file: UploadFile = File(...)):
    try:
        document = await process_upload(file)
        message = (
            "Document uploaded, chunked, and indexed successfully"
            if getattr(document, "indexing_status", None) == "indexed"
            else "Document uploaded and chunked, but vector indexing failed."
        )
        return UploadSuccessResponse(message=message, document=document)
    except DocumentProcessingError as exc:
        logger.error("Upload failed: %s — %s", exc.message, exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "details": exc.details,
            },
        )
    except Exception as exc:
        logger.exception("Unexpected upload error")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An unexpected error occurred while processing the upload.",
                "details": str(exc),
            },
        )


@router.get("/documents", response_model=DocumentsListResponse)
def get_documents():
    return DocumentsListResponse(documents=list_documents())


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def search_documents(
    payload: SearchRequest,
    retriever: SemanticRetriever = Depends(get_retriever),
):
    try:
        retrieved_chunks = retriever.retrieve_with_scores(
            question=payload.query,
            top_k=payload.n_results,
        )
    except ValueError as exc:
        logger.warning("Invalid search request: %s", exc)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid search request.",
                "details": str(exc),
            },
        )
    except Exception as exc:
        logger.exception("Semantic search failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An unexpected error occurred during retrieval.",
                "details": str(exc),
            },
        )

    results = []
    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata") or {}
        document_id = metadata.get("document_id") or metadata.get("id") or chunk.get("document_name", "unknown")
        chunk_id = metadata.get("chunk_id") or f"{document_id}:{chunk.get('chunk_index', 0)}"
        results.append(
            SearchResult(
                chunk_id=str(chunk_id),
                document_id=str(document_id),
                document_name=str(chunk.get("document_name", "Unknown")),
                chunk_index=int(chunk.get("chunk_index", 0)),
                content=str(chunk.get("text", "")),
                score=float(chunk.get("score", 0.0)),
            )
        )

    return SearchResponse(query=payload.query, results=results, total=len(results))
