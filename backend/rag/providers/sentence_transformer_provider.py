"""
sentence_transformer_provider.py — SentenceTransformers Embedding Provider.

Implements the EmbeddingProvider interface using the `sentence-transformers` library.
This is the default, locally-running provider for the Universal Context Engine.

Key characteristics:
  - Lazy initialization: model is loaded only on the first embedding call
  - Thread-safe: double-checked locking prevents duplicate model loads
  - Memory efficient: model is loaded exactly once per process lifetime
  - Zero numpy in output: all return values are pure Python lists

Design Principles Applied:
  - Single Responsibility Principle (SRP): only responsibility is generating embeddings
  - Liskov Substitution Principle (LSP): fully substitutable for EmbeddingProvider
  - Dependency Inversion Principle (DIP): depends on the abstract base, not on callers
"""

import logging
import threading
from typing import List, Optional

from rag.providers.base_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Embedding provider backed by the `sentence-transformers` library.

    Uses `all-MiniLM-L6-v2` by default — a compact (80 MB) model that produces
    384-dimensional embeddings with strong semantic quality for English text.

    Thread Safety
    -------------
    Model loading is protected by a class-level threading.Lock. The double-checked
    locking pattern ensures the lock is only acquired on the very first call,
    making subsequent calls lock-free.

    Usage
    -----
        provider = SentenceTransformerProvider()
        vector = provider.embed_text("Hello, World!")       # List[float], len=384
        vectors = provider.embed_documents(["A", "B", "C"]) # List[List[float]]
    """

    _PROVIDER_NAME: str = "sentence-transformers"
    _DEFAULT_MODEL: str = "all-MiniLM-L6-v2"

    # Class-level lock shared across all instances — prevents multi-thread model load races
    _load_lock: threading.Lock = threading.Lock()

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        """
        Prepare the provider. The model is NOT loaded here — only on first use.

        Args:
            model_name: The sentence-transformers model identifier.
                        Defaults to 'all-MiniLM-L6-v2'.
        """
        self._model_name: str = model_name
        # _model is intentionally None until _ensure_model_loaded() is called
        self._model: Optional[object] = None
        logger.info(
            "SentenceTransformerProvider initialised (model will be loaded on first use): %s",
            self._model_name,
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
        """Return the model identifier this provider is configured to use."""
        return self._model_name

    # ------------------------------------------------------------------
    # Internal: lazy, thread-safe model loading
    # ------------------------------------------------------------------

    def _ensure_model_loaded(self) -> None:
        """
        Load the SentenceTransformer model if it has not been loaded yet.

        Implements the double-checked locking pattern:
          1. First check (without lock) — fast path for already-loaded model
          2. Acquire lock only if model is not yet loaded
          3. Second check (inside lock) — prevents duplicate loading when two
             threads both pass the first check simultaneously

        Raises:
            RuntimeError: If the model fails to load for any reason.
        """
        # Fast path — model already loaded, no lock needed
        if self._model is not None:
            return

        with self._load_lock:
            # Second check inside lock — another thread may have loaded while we waited
            if self._model is not None:
                return

            logger.info(
                "Loading SentenceTransformer model: %s (this happens once per process)",
                self._model_name,
            )

            try:
                # Import deferred to here so the module can be imported even when
                # sentence-transformers is not installed (fail only on actual use)
                from sentence_transformers import SentenceTransformer  # type: ignore

                self._model = SentenceTransformer(self._model_name)
                logger.info(
                    "SentenceTransformer model loaded successfully: %s",
                    self._model_name,
                )
            except ImportError as exc:
                logger.error(
                    "sentence-transformers package is not installed. "
                    "Run: pip install sentence-transformers"
                )
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Add it to requirements.txt and reinstall."
                ) from exc
            except Exception as exc:
                logger.exception(
                    "Failed to load SentenceTransformer model '%s': %s",
                    self._model_name,
                    exc,
                )
                raise RuntimeError(
                    f"Model '{self._model_name}' could not be loaded: {exc}"
                ) from exc

    # ------------------------------------------------------------------
    # Input validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_text_input(text: object) -> None:
        """
        Validate that embed_text received an acceptable argument.

        Args:
            text: The value passed to embed_text().

        Raises:
            ValueError: If text is None or not a string.
        """
        if text is None:
            raise ValueError(
                "embed_text() received None. "
                "A string is required (pass an empty string '' to get an empty embedding)."
            )
        if not isinstance(text, str):
            raise ValueError(
                f"embed_text() expected str, got {type(text).__name__}."
            )

    @staticmethod
    def _validate_documents_input(texts: object) -> None:
        """
        Validate that embed_documents received an acceptable argument.

        Args:
            texts: The value passed to embed_documents().

        Raises:
            ValueError: If texts is None or not a list.
        """
        if texts is None:
            raise ValueError(
                "embed_documents() received None. "
                "A list of strings is required."
            )
        if not isinstance(texts, list):
            raise ValueError(
                f"embed_documents() expected list, got {type(texts).__name__}."
            )

    # ------------------------------------------------------------------
    # Core embedding methods
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a dense vector.

        The model is loaded on the first call (lazy initialization).

        Args:
            text: Input text to embed. Must be a non-None string.
                  An empty string returns an empty list without calling the model.

        Returns:
            A Python list of floats (length = model embedding dimension, e.g. 384).
            Returns [] if text is empty after stripping.

        Raises:
            ValueError: If text is None or not a string.
            RuntimeError: If the model fails to load or inference fails.
        """
        self._validate_text_input(text)

        if not text.strip():
            logger.warning("embed_text() called with empty string — returning empty list.")
            return []

        logger.info("Embedding request: single text (%d characters)", len(text))

        self._ensure_model_loaded()

        try:
            # encode() returns a numpy ndarray — convert to plain Python list immediately
            raw_embedding = self._model.encode(text, convert_to_numpy=True)  # type: ignore[union-attr]
            embedding: List[float] = raw_embedding.tolist()
            logger.info(
                "Embedding generated: dimension=%d",
                len(embedding),
            )
            return embedding
        except Exception as exc:
            logger.exception("Unexpected error during text embedding: %s", exc)
            raise RuntimeError(
                f"Embedding inference failed for input text: {exc}"
            ) from exc

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings into dense vectors.

        The model is loaded on the first call (lazy initialization).
        Batching through the model in one call is significantly faster than
        calling embed_text() in a loop.

        Args:
            texts: List of input strings. Each item must be a string.
                   Empty strings in the batch are replaced with empty lists
                   without being sent to the model.

        Returns:
            A list of embedding vectors (List[List[float]]), in the same order
            as the input texts. Empty input strings yield empty sublists [].

        Raises:
            ValueError: If texts is None or not a list.
            RuntimeError: If the model fails to load or batch inference fails.
        """
        self._validate_documents_input(texts)

        if not texts:
            logger.warning("embed_documents() called with empty list — returning [].")
            return []

        logger.info(
            "Embedding request: batch of %d documents",
            len(texts),
        )

        # Separate empty texts (they won't go to model) from non-empty ones
        non_empty_indices: List[int] = []
        non_empty_texts: List[str] = []

        for idx, text in enumerate(texts):
            if isinstance(text, str) and text.strip():
                non_empty_indices.append(idx)
                non_empty_texts.append(text)

        # Pre-fill results with empty lists — empty texts stay as []
        results: List[List[float]] = [[] for _ in texts]

        if not non_empty_texts:
            logger.warning(
                "embed_documents() — all %d texts were empty, returning list of empty lists.",
                len(texts),
            )
            return results

        self._ensure_model_loaded()

        try:
            # Batch encode: returns numpy array of shape (n, embedding_dim)
            raw_embeddings = self._model.encode(  # type: ignore[union-attr]
                non_empty_texts,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            # Map embeddings back to their original positions in the input list
            for position, original_index in enumerate(non_empty_indices):
                results[original_index] = raw_embeddings[position].tolist()

            logger.info(
                "Batch embedding complete: %d documents embedded, dimension=%d",
                len(non_empty_texts),
                len(results[non_empty_indices[0]]) if non_empty_indices else 0,
            )
            return results

        except Exception as exc:
            logger.exception("Unexpected error during batch embedding: %s", exc)
            raise RuntimeError(
                f"Batch embedding inference failed: {exc}"
            ) from exc
