"""
base_provider.py — Abstract Embedding Provider Interface.

Defines the contract that every embedding provider MUST satisfy.
No implementation details leak into this file.

Design Principles Applied:
  - Interface Segregation Principle (ISP): methods are focused and minimal
  - Dependency Inversion Principle (DIP): consumers depend on this abstraction, not on concrete classes
  - Open/Closed Principle (OCP): new providers extend this class without modifying it
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """
    Abstract base class for all embedding providers in the Universal Context Engine.

    Any class that converts text into dense vector representations must implement
    this interface. The rest of the system only ever interacts with this type,
    never with concrete implementations.

    Concrete implementations must override:
        - provider_name (property)
        - model_name (property)
        - embed_text(text)
        - embed_documents(texts)
    """

    # ------------------------------------------------------------------
    # Identity properties — used for logging and introspection
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable name of the embedding backend.

        Examples: "sentence-transformers", "openai", "gemini"
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Name of the specific model this provider uses.

        Examples: "all-MiniLM-L6-v2", "text-embedding-3-small"
        """

    # ------------------------------------------------------------------
    # Core embedding methods
    # ------------------------------------------------------------------

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Convert a single text string into a dense embedding vector.

        Args:
            text: The input text to embed. Must not be None.

        Returns:
            A list of floats representing the embedding vector.
            Returns an empty list if the text is empty.

        Raises:
            ValueError: If text is None or the input type is invalid.
        """

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a batch of text strings into embedding vectors.

        Args:
            texts: A list of input texts to embed. Must not be None.
                   Individual texts may be empty strings — the provider
                   must handle them gracefully.

        Returns:
            A list of embedding vectors, one per input text, in the same order.

        Raises:
            ValueError: If texts is None or not a list.
        """
