import logging
from functools import lru_cache
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from config import get_settings
from models.schemas import ErrorResponse, RetrievalHealthResponse, RetrievalRequest, RetrievalResponse, RetrievalResult
from rag.embedding_service import EmbeddingService
from rag.retriever import SemanticRetriever
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/retrieval", tags=["Retrieval"])


class RetrievalService:
    """Thin application service that orchestrates semantic retrieval."""

    def __init__(self, retriever: SemanticRetriever) -> None:
        if retriever is None:
            raise ValueError("retriever cannot be None")
        self._retriever = retriever

    def search(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if question is None:
            raise ValueError("Question cannot be None")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question cannot be empty or whitespace-only")
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        return self._retriever.retrieve_with_scores(question=question, top_k=top_k)

    def health_check(self) -> Dict[str, str]:
        try:
            health_state = self._retriever.health_check()
            if health_state != "PASS":
                return {
                    "status": "degraded",
                    "embedding_service": "unavailable",
                    "vector_store": "unavailable",
                    "retriever": "unavailable",
                }

            return {
                "status": "healthy",
                "embedding_service": "available",
                "vector_store": "available",
                "retriever": "available",
            }
        except Exception as exc:
            logger.exception("Retrieval health check failed")
            return {
                "status": "unhealthy",
                "embedding_service": "unavailable",
                "vector_store": "unavailable",
                "retriever": "unavailable",
                "details": str(exc),
            }


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


@lru_cache
def get_retrieval_service(
    retriever: SemanticRetriever = Depends(get_retriever),
) -> RetrievalService:
    return RetrievalService(retriever=retriever)


@router.post(
    "/search",
    response_model=RetrievalResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def search_retrieval(
    payload: RetrievalRequest,
    service: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalResponse:
    try:
        chunks = service.search(question=payload.question, top_k=payload.top_k)
    except ValueError as exc:
        logger.warning("Invalid retrieval request: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Retrieval search failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    results = [
        RetrievalResult(
            document_name=str(chunk.get("document_name", "Unknown")),
            chunk_index=int(chunk.get("chunk_index", 0)),
            score=float(chunk.get("score", 0.0)),
            text=str(chunk.get("text", "")),
        )
        for chunk in chunks
    ]
    return RetrievalResponse(results=results)


@router.get(
    "/health",
    response_model=RetrievalHealthResponse,
    responses={500: {"model": ErrorResponse}},
)
def health_retrieval(
    service: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalHealthResponse:
    return RetrievalHealthResponse(**service.health_check())
