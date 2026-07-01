"""
openai_provider.py — OpenAI Embedding Provider (Placeholder).

This module reserves the integration point for the OpenAI Embeddings API.
It satisfies the EmbeddingProvider interface but raises NotImplementedError
until the OpenAI integration is built in a future module.

Design Principles Applied:
  - Liskov Substitution Principle (LSP): structurally compatible with EmbeddingProvider
  - Single Responsibility Principle (SRP): this file's only job is to define this placeholder
"""

import logging
from typing import List

from rag.providers.base_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder embedding provider for the OpenAI Embeddings API.

    This class exists to complete the provider registry so the factory
    can resolve "openai" as a valid (future) provider name.
    It will be implemented in a future module when OpenAI integration
    is added to the Universal Context Engine.
    """

    _PROVIDER_NAME: str = "openai"
    _DEFAULT_MODEL: str = "text-embedding-3-small"
    _NOT_IMPLEMENTED_MSG: str = (
        "OpenAI embedding provider will be implemented in future versions."
    )

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        """
        Initialise the placeholder provider.

        Args:
            model_name: Reserved for future use. Stored but never called.
        """
        self._model_name = model_name
        logger.warning(
            "OpenAIEmbeddingProvider is a placeholder. "
            "All calls will raise NotImplementedError."
        )

    # ------------------------------------------------------------------
    # Identity properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Return the canonical name of this provider."""
        return self._PROVIDER_NAME

    @property
    def model_name(self) -> str:
        """Return the configured model name."""
        return self._model_name

    # ------------------------------------------------------------------
    # Core embedding methods — intentionally not implemented
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        """
        Not implemented. Raises NotImplementedError.

        Raises:
            NotImplementedError: Always. OpenAI integration is pending.
        """
        raise NotImplementedError(self._NOT_IMPLEMENTED_MSG)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Not implemented. Raises NotImplementedError.

        Raises:
            NotImplementedError: Always. OpenAI integration is pending.
        """
        raise NotImplementedError(self._NOT_IMPLEMENTED_MSG)
