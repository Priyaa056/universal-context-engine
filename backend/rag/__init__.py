"""
RAG (Retrieval-Augmented Generation) package for the Universal Context Engine.

This package is structured in isolated, replaceable modules:
  - providers/   : Embedding provider implementations (SentenceTransformers, OpenAI, Gemini)
  - embedding_factory.py : Factory that resolves provider name → provider instance
  - embedding_service.py : Thin orchestration layer; the only public API of this package
"""
