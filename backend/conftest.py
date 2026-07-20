"""
conftest.py — Session-scoped pytest configuration for the Universal Context Engine.

IMPORTANT: this file must not be imported by production code. It is loaded
automatically by pytest and is invisible to the FastAPI application at runtime.

Purpose
-------
The ``SentenceTransformerProvider`` loads a ~90 MB HuggingFace model during
``__init__``, which fails in low-memory / small-paging-file CI environments
with OSError 1455 ("The paging file is too small ...").

The patch below replaces the model-loading step with a deterministic stub that
returns a fixed-dimension embedding vector. The stub is only active while pytest
is running; it has no effect on the production application.

The stub produces a *consistent* 384-dimensional vector per input string (same
string → same vector) so that Chroma can index and retrieve documents without
needing a real ML model.
"""

import hashlib
import math
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Lightweight embedding stub
# ---------------------------------------------------------------------------

_STUB_DIM = 384  # matches all-MiniLM-L6-v2 output dimension


def _stub_embed(text: str):
    """Return a deterministic unit-length vector for *text*.

    The vector is derived from a SHA-256 hash so the same string always
    produces the same vector, giving Chroma a stable nearest-neighbour
    ordering even without the real model.
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Build raw floats from repeated bytes
    raw = []
    for i in range(_STUB_DIM):
        raw.append(float(digest[i % len(digest)]) / 255.0 - 0.5)

    # Normalise to unit length
    magnitude = math.sqrt(sum(v * v for v in raw)) or 1.0
    return [v / magnitude for v in raw]


# ---------------------------------------------------------------------------
# Patch applied for the entire test session
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="session")
def _patch_sentence_transformer():
    """
    Autouse session fixture that replaces SentenceTransformerProvider's model
    loading with a lightweight stub.

    This fixture runs before any test and tears down after the last test.
    Production code is completely unaffected.
    """
    from rag.providers.sentence_transformer_provider import SentenceTransformerProvider

    def _stub_ensure_model_loaded(self):
        """Skip the real model load; install stub callables instead."""
        if getattr(self, "_model", None) is not None:
            return  # already "loaded"
        # Install a minimal object that has the encode() interface
        self._model = _StubModel()

    class _StubModel:
        def encode(self, texts, **kwargs):
            if isinstance(texts, str):
                return [_stub_embed(texts)]
            return [_stub_embed(t) for t in texts]

    with patch.object(
        SentenceTransformerProvider,
        "_ensure_model_loaded",
        _stub_ensure_model_loaded,
    ):
        yield
