"""
embedding_factory.py — Embedding Provider Factory.

Single function that maps a provider name string → an EmbeddingProvider instance.
This is the only place in the codebase that knows which concrete providers exist.

Design Principles Applied:
  - Single Responsibility Principle (SRP): one job — resolve provider name to instance
  - Open/Closed Principle (OCP): add a new provider by adding one line to _PROVIDER_REGISTRY
  - Factory Pattern: creation logic is centralized and hidden from callers
  - Dependency Inversion: callers depend on EmbeddingProvider, not on concrete classes
"""

import logging
from typing import Dict, Type

from rag.providers.base_provider import EmbeddingProvider
from rag.providers.gemini_provider import GeminiEmbeddingProvider
from rag.providers.openai_provider import OpenAIEmbeddingProvider
from rag.providers.sentence_transformer_provider import SentenceTransformerProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------
# Maps the canonical provider name (used in config / env) to its class.
# To add a new provider: import its class and add one entry here.
# Nothing else needs to change.
# ---------------------------------------------------------------------------
_PROVIDER_REGISTRY: Dict[str, Type[EmbeddingProvider]] = {
    "sentence-transformers": SentenceTransformerProvider,
    "openai": OpenAIEmbeddingProvider,
    "gemini": GeminiEmbeddingProvider,
}


def get_embedding_provider(
    provider_name: str,
    model_name: str,
) -> EmbeddingProvider:
    """
    Resolve a provider name to a concrete EmbeddingProvider instance.

    This is the single point of coupling between provider names (strings from
    configuration) and provider classes (Python objects). Callers never import
    concrete provider classes directly.

    Args:
        provider_name: The canonical name of the desired provider.
                       Supported values: "sentence-transformers", "openai", "gemini".
                       Matching is case-sensitive to avoid subtle config bugs.
        model_name:    The model identifier to pass to the chosen provider.
                       What constitutes a valid model name is provider-specific.

    Returns:
        A fully-initialised EmbeddingProvider instance ready to embed text.

    Raises:
        ValueError: If provider_name does not match any registered provider.
                    The error message lists all supported provider names.

    Example:
        >>> provider = get_embedding_provider("sentence-transformers", "all-MiniLM-L6-v2")
        >>> vector = provider.embed_text("Hello, World!")
    """
    logger.info(
        "Embedding provider requested: provider='%s', model='%s'",
        provider_name,
        model_name,
    )

    provider_class = _PROVIDER_REGISTRY.get(provider_name)

    if provider_class is None:
        supported = ", ".join(f"'{name}'" for name in _PROVIDER_REGISTRY)
        raise ValueError(
            f"Unknown embedding provider: '{provider_name}'. "
            f"Supported providers: {supported}. "
            f"Check the EMBEDDING_PROVIDER environment variable."
        )

    logger.info(
        "Resolved provider '%s' → %s",
        provider_name,
        provider_class.__name__,
    )

    instance = provider_class(model_name=model_name)

    logger.info(
        "EmbeddingProvider instance created: class=%s, model=%s",
        provider_class.__name__,
        model_name,
    )

    return instance
