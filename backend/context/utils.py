from typing import Any, Dict, List, Optional


def normalize_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts the fields needed by the context builder from a retrieval result."""
    metadata = chunk.get("metadata") or {}
    return {
        "text": chunk.get("text") or "",
        "score": float(chunk.get("score", 0.0) or 0.0),
        "document_id": chunk.get("document_id") or metadata.get("document_id", ""),
        "filename": chunk.get("filename") or metadata.get("filename", ""),
        "chunk_index": chunk.get("chunk_index") if chunk.get("chunk_index") is not None else int(metadata.get("chunk_index", 0) or 0),
    }


def deduplicate_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes exact duplicate chunk texts while preserving the highest-scoring occurrence."""
    unique_by_text: Dict[str, Dict[str, Any]] = {}

    for chunk in chunks:
        text = chunk.get("text") or ""
        if not text:
            continue

        existing = unique_by_text.get(text)
        if existing is None:
            unique_by_text[text] = chunk
        elif chunk.get("score", 0.0) > existing.get("score", 0.0):
            unique_by_text[text] = chunk

    return list(unique_by_text.values())
