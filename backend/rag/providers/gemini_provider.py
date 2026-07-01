"""
gemini_provider.py — Google Gemini Embedding Provider (Placeholder).

This module reserves the integration point for the Google Gemini Embeddings API.
It satisfies the EmbeddingProvider interface but raises NotImplementedError
until the Gemini integration is built in a future module.

Design Principles Applied:
  - Liskov Substitution Principle (LSP): structurally compatible with EmbeddingProvider
  - Single Responsibility Principle (SRP): this file's only job is to define this placeholder
"""

import logging
from typing import List

from rag.providers.base_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder embedding provider for the Google Gemini Embeddings API.

    This class exists to complete the provider registry so the factory
    can resolve "gemini" as a valid (future) provider name.
    It will be implemented in a future module when Gemini integration
    is added to the Universal Context Engine.
    """

    _PROVIDER_NAME: str = "gemini"
    _DEFAULT_MODEL: str = "models/text-embedding-004"
    _NOT_IMPLEMENTED_MSG: str = (
        "Gemini embedding provider will be implemented in future versions."
    )

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        """
        Initialise the placeholder provider.

        Args:
            model_name: Reserved for future use. Stored but never called.
        """
        self._model_name = model_name
        logger.warning(
            "GeminiEmbeddingProvider is a placeholder. "
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
            NotImplementedError: Always. Gemini integration is pending.
        """
        raise NotImplementedError(self._NOT_IMPLEMENTED_MSG)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Not implemented. Raises NotImplementedError.

        Raises:
            NotImplementedError: Always. Gemini integration is pending.
        """
        raise NotImplementedError(self._NOT_IMPLEMENTED_MSG)
