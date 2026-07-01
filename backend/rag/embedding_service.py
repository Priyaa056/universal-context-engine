"""
embedding_service.py — Embedding Service (Public API of the RAG package).

This is the ONLY module that outside code should import from the `rag` package
when it needs to generate embeddings. It acts as a thin orchestration layer
between the application and the embedding infrastructure.

What this service KNOWS about:
  - The EmbeddingProvider interface
  - The EmbeddingFactory (to resolve provider by name)
  - Application configuration (Settings)

What this service DOES NOT KNOW about:
  - ChromaDB / vector stores
  - Retrieval logic
  - Document upload or chunking
  - LLM or chat
  - HTTP / FastAPI
  - Any specific provider implementation

Design Principles Applied:
  - Single Responsibility Principle (SRP): only orchestrates embedding calls
  - Dependency Inversion (DIP): depends on the abstract EmbeddingProvider, not concrete classes
  - Facade Pattern: simple interface over the provider + factory complexity
"""

import logging
from typing import List

from config import get_settings
from rag.embedding_factory import get_embedding_provider
from rag.providers.base_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    High-level embedding service for the Universal Context Engine.

    Wraps an EmbeddingProvider and exposes a clean, stable API that the rest
    of the application depends on. When the underlying provider changes (e.g.,
    from sentence-transformers to OpenAI), only the configuration changes —
    no calling code needs to be updated.

    Attributes:
        provider_name (str): The name of the active embedding backend.
        model_name    (str): The name of the model in use.

    Usage:
        service = EmbeddingService()
        vector  = service.embed_text("What is the capital of France?")
        vectors = service.embed_documents(["Paris", "London", "Berlin"])
    """

    def __init__(
        self,
        provider_name: str | None = None,
        model_name: str | None = None,
    ) -> None:
        """
        Initialise the EmbeddingService.

        Provider and model are resolved from application settings if not supplied.
        This enables the same constructor to work in tests (explicit arguments)
        and in production (reads from environment via Settings).

        Args:
            provider_name: Override the provider from settings. Useful in tests.
            model_name:    Override the model from settings. Useful in tests.

        Raises:
            ValueError:   If the resolved provider_name is not supported.
            RuntimeError: If the provider fails to initialise.
        """
        settings = get_settings()

        # Use explicit args when provided, fall back to global settings
        resolved_provider = provider_name or settings.EMBEDDING_PROVIDER
        resolved_model = model_name or settings.EMBEDDING_MODEL_NAME

        logger.info(
            "EmbeddingService starting: provider='%s', model='%s'",
            resolved_provider,
            resolved_model,
        )

        self._provider: EmbeddingProvider = get_embedding_provider(
            provider_name=resolved_provider,
            model_name=resolved_model,
        )

        logger.info(
            "EmbeddingService ready: provider='%s', model='%s'",
            self._provider.provider_name,
            self._provider.model_name,
        )

    # ------------------------------------------------------------------
    # Identity properties — for logging, health checks, and test introspection
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Return the name of the active embedding provider."""
        return self._provider.provider_name

    @property
    def model_name(self) -> str:
        """Return the name of the model in use."""
        return self._provider.model_name

    # ------------------------------------------------------------------
    # Public embedding interface
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.

        Delegates directly to the underlying provider. All validation and
        error handling is performed inside the provider.

        Args:
            text: The input text to embed. Must be a non-None string.

        Returns:
            A list of floats representing the embedding vector.
            Returns [] if the input text is empty.

        Raises:
            ValueError:   If text is None or not a string.
            RuntimeError: If embedding inference fails.
        """
        logger.info(
            "EmbeddingService.embed_text() called: %d characters",
            len(text) if isinstance(text, str) else 0,
        )

        embedding = self._provider.embed_text(text)

        logger.info(
            "EmbeddingService.embed_text() complete: dimension=%d",
            len(embedding),
        )

        return embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings.

        Delegates directly to the underlying provider. All validation and
        error handling is performed inside the provider.

        Args:
            texts: A list of input strings to embed.

        Returns:
            A list of embedding vectors, one per input text, in the same order.

        Raises:
            ValueError:   If texts is None or not a list.
            RuntimeError: If batch inference fails.
        """
        count = len(texts) if isinstance(texts, list) else 0
        logger.info(
            "EmbeddingService.embed_documents() called: %d documents",
            count,
        )

        embeddings = self._provider.embed_documents(texts)

        logger.info(
            "EmbeddingService.embed_documents() complete: %d embeddings returned",
            len(embeddings),
        )

        return embeddings
