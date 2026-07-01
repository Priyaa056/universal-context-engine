import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application configuration for the Universal Context Engine.

    All values are read from environment variables so that no secrets or
    environment-specific settings are ever hardcoded. Sensible defaults are
    provided for local development.
    """

    # ------------------------------------------------------------------
    # Application identity
    # ------------------------------------------------------------------
    APP_TITLE: str = "Universal Context Engine"
    APP_VERSION: str = "1.0.0"

    # ------------------------------------------------------------------
    # External API keys (optional — only required by future providers)
    # ------------------------------------------------------------------
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ------------------------------------------------------------------
    # Embedding layer (Phase 3 — Module 1)
    # ------------------------------------------------------------------
    # The provider name must match a key in embedding_factory._PROVIDER_REGISTRY.
    # Changing this env var swaps the entire embedding backend with zero code changes.
    EMBEDDING_PROVIDER: str = os.getenv(
        "EMBEDDING_PROVIDER", "sentence-transformers"
    )

    # The model name is passed directly to the chosen provider.
    # For sentence-transformers this is a HuggingFace model identifier.
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"
    )

    # ------------------------------------------------------------------
    # Vector storage (Phase 3 — Module 2)
    # ------------------------------------------------------------------
    # Directory where ChromaDB persists its on-disk data.
    # Relative paths are resolved from the backend/ root at runtime.
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")

    # Default number of semantic search results returned by /kb/search.
    SEARCH_N_RESULTS: int = int(os.getenv("SEARCH_N_RESULTS", "5"))


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()

