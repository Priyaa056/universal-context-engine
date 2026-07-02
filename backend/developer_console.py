import json
import os
import sys
from pathlib import Path

from rag.embedding_service import EmbeddingService
from rag.retriever import SemanticRetriever
from rag.vector_store import VectorStore

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_FILE = DATA_DIR / "documents.json"
CHUNKS_FILE = DATA_DIR / "chunks.json"


def _load_json(path: Path, default=None):
    if default is None:
        default = []
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}")
        return default


def _print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def show_uploaded_documents() -> None:
    _print_header("Uploaded Documents")
    documents = _load_json(DOCUMENTS_FILE, [])
    if not documents:
        print("No uploaded documents found.")
        return

    for doc in documents:
        print(f"- filename: {doc.get('filename', '<unknown>')}")
        print(f"  file_type: {doc.get('file_type', 'unknown')}")
        print(f"  chunks_created: {doc.get('chunks_created', 0)}")
        print(f"  indexed_chunks: {doc.get('indexed_chunks', 0)}")
        print(f"  upload_time: {doc.get('uploaded_at', 'unknown')}")
        print(f"  indexing_status: {doc.get('indexing_status', 'unknown')}")
        print()


def show_stored_chunks() -> None:
    _print_header("Stored Chunks")
    chunks = _load_json(CHUNKS_FILE, [])
    if not chunks:
        print("No stored chunks found.")
        return

    for chunk in chunks:
        text = chunk.get("content", "") or ""
        preview = text[:200].replace("\n", " ")
        print(f"- document: {chunk.get('document_name', '<unknown>')}")
        print(f"  chunk_index: {chunk.get('chunk_index', 0)}")
        print(f"  length: {len(text)}")
        print(f"  preview: {preview}")
        print()


def inspect_document_chunks() -> None:
    _print_header("Inspect Document Chunks")
    filename = input("Enter filename: ").strip()
    if not filename:
        print("No filename entered.")
        return

    chunks = _load_json(CHUNKS_FILE, [])
    matching = [chunk for chunk in chunks if chunk.get("document_name") == filename]
    if not matching:
        print(f"No chunks found for document: {filename}")
        return

    for chunk in matching:
        text = chunk.get("content", "") or ""
        print(f"- chunk_index: {chunk.get('chunk_index', 0)}")
        print(f"  length: {len(text)}")
        print("  text:")
        print(text)
        print()


def show_chroma_collection_info() -> None:
    _print_header("ChromaDB Collection Info")
    try:
        vector_store = VectorStore()
        info = vector_store.get_collection_info()
    except Exception as exc:
        print(f"Unable to read ChromaDB collection: {exc}")
        return

    print(f"collection_name: {info.get('name', '<unknown>')}")
    print(f"count: {info.get('count', 0)}")
    print(f"storage_path: {vector_store.persist_directory}")


def run_semantic_search_demo() -> None:
    _print_header("Semantic Search Demo")
    question = input("Enter question: ").strip()
    if not question:
        print("Question cannot be empty.")
        return

    top_k_input = input("Enter top_k (default 5): ").strip()
    top_k = int(top_k_input) if top_k_input.isdigit() else 5

    try:
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        retriever = SemanticRetriever(embedding_service=embedding_service, vector_store=vector_store)
        results = retriever.retrieve_with_scores(question=question, top_k=top_k)
    except Exception as exc:
        print(f"Semantic search failed: {exc}")
        return

    if not results:
        print("No results found in ChromaDB.")
        return

    for index, result in enumerate(results, start=1):
        print(f"{index}. score={result.get('score', 0.0)}")
        print(f"   document_name: {result.get('document_name', '<unknown>')}")
        print(f"   chunk_index: {result.get('chunk_index', 0)}")
        print("   text:")
        print(result.get('text', ''))
        print()


def main() -> None:
    while True:
        print("\nUniversal Context Engine Developer Console")
        print("1. Show uploaded documents")
        print("2. Show stored chunks from data/chunks.json")
        print("3. Inspect one document's chunks")
        print("4. Show ChromaDB collection info")
        print("5. Run semantic search demo")
        print("6. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            show_uploaded_documents()
        elif choice == "2":
            show_stored_chunks()
        elif choice == "3":
            inspect_document_chunks()
        elif choice == "4":
            show_chroma_collection_info()
        elif choice == "5":
            run_semantic_search_demo()
        elif choice == "6":
            print("Exiting developer console.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
