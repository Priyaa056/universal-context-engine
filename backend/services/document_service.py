import json
import logging
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from config import get_settings
from models.schemas import ChunkRecord, DocumentMetadata, DocumentSummary
from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from services.chunking_service import chunk_text
from services.formatting_service import format_file_size, format_uploaded_at, now_utc
from services.metadata_service import generate_document_id

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_FILE = DATA_DIR / "documents.json"
CHUNKS_FILE = DATA_DIR / "chunks.json"


class DocumentProcessingError(Exception):
    """Raised when document upload or extraction fails."""

    def __init__(self, message: str, details: str, status_code: int = 400):
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


def _ensure_directories() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default: list) -> list:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_json(path: Path, data: list) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, default=str)


def _validate_file(filename: str | None) -> tuple[str, str]:
    if not filename:
        raise DocumentProcessingError(
            message="No file selected.",
            details="Upload request did not include a filename.",
        )

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(
            message="Unsupported file type.",
            details=f"Received file with extension '{extension or 'none'}'.",
        )

    file_type = extension.lstrip(".")
    return filename, file_type


def _extract_text_from_txt(file_path: Path) -> str:
    logger.info("Extracting text from TXT: %s", file_path.name)
    return file_path.read_text(encoding="utf-8", errors="replace")


def _extract_text_from_pdf(file_path: Path) -> str:
    if not file_path.exists():
        raise DocumentProcessingError(
            message="Unable to process PDF.",
            details=f"Saved file not found at {file_path}.",
        )

    logger.info("Opening PDF: %s (size=%d bytes)", file_path.name, file_path.stat().st_size)

    try:
        reader = PdfReader(str(file_path), strict=False)
    except (PdfReadError, PdfStreamError) as exc:
        logger.exception("Failed to open PDF: %s", file_path.name)
        raise DocumentProcessingError(
            message="Unable to extract text from PDF.",
            details=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error opening PDF: %s", file_path.name)
        raise DocumentProcessingError(
            message="Unable to extract text from PDF.",
            details=str(exc),
        ) from exc

    page_count = len(reader.pages)
    logger.info("PDF opened: %s, pages=%d", file_path.name, page_count)

    if page_count == 0:
        raise DocumentProcessingError(
            message="Unable to extract text from PDF.",
            details="PDF contains no pages.",
        )

    page_texts: list[str] = []

    for index, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
        except Exception as exc:
            logger.warning(
                "Failed to extract text from page %d of %s: %s",
                index,
                file_path.name,
                exc,
            )
            continue

        if page_text is None:
            logger.debug("Page %d of %s returned no text", index, file_path.name)
            continue

        cleaned = page_text.strip()
        if cleaned:
            page_texts.append(cleaned)
            logger.debug(
                "Page %d of %s: extracted %d characters",
                index,
                file_path.name,
                len(cleaned),
            )

    text = "\n".join(page_texts)
    logger.info(
        "PDF text extracted: %s, pages_with_text=%d, total_chars=%d",
        file_path.name,
        len(page_texts),
        len(text),
    )

    if not text.strip():
        raise DocumentProcessingError(
            message="Unable to extract text from PDF.",
            details="PDF contains no extractable text. It may be image-only or empty.",
        )

    return text


def _extract_text(file_path: Path, file_type: str) -> str:
    if file_type == "txt":
        return _extract_text_from_txt(file_path)
    if file_type == "pdf":
        return _extract_text_from_pdf(file_path)
    raise DocumentProcessingError(
        message="Unsupported file type.",
        details=f"Cannot extract text for file type '{file_type}'.",
    )


def _remove_existing_document(filename: str) -> None:
    documents = _load_json(DOCUMENTS_FILE, [])
    chunks = _load_json(CHUNKS_FILE, [])

    matching_ids = {doc.get("id") for doc in documents if doc["filename"] == filename}
    documents = [doc for doc in documents if doc["filename"] != filename]
    chunks = [
        chunk
        for chunk in chunks
        if chunk["document_name"] != filename
        and chunk.get("document_id") not in matching_ids
    ]

    _save_json(DOCUMENTS_FILE, documents)
    _save_json(CHUNKS_FILE, chunks)


def _cleanup_upload(file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink(missing_ok=True)
        logger.info("Removed failed upload: %s", file_path.name)


def _index_chunks_in_vector_store(
    document_id: str,
    filename: str,
    file_type: str,
    chunks: list[str],
    upload_time: str,
) -> tuple[int, str]:
    try:
        settings = get_settings()
        embedding_service = EmbeddingService(
            provider_name=settings.EMBEDDING_PROVIDER,
            model_name=settings.EMBEDDING_MODEL_NAME,
        )
        vector_store = VectorStore(persist_directory=settings.CHROMA_PERSIST_DIR)
        embeddings = embedding_service.embed_documents(chunks)

        ids = [f"{document_id}_chunk_{index}" for index in range(len(chunks))]
        metadatas = [
            {
                "document_id": document_id,
                "filename": filename,
                "file_type": file_type,
                "chunk_index": index,
                "upload_time": upload_time,
            }
            for index in range(len(chunks))
        ]

        vector_store.add_documents(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        logger.info("Indexed %d chunks into ChromaDB for %s", len(chunks), filename)
        return len(chunks), "indexed"
    except Exception as exc:
        logger.exception("Vector indexing failed for %s", filename)
        return 0, "indexing_failed"


def list_documents() -> list[DocumentSummary]:
    _ensure_directories()
    documents = _load_json(DOCUMENTS_FILE, [])

    return [
        DocumentSummary(
            id=str(doc.get("id", doc.get("filename", ""))),
            filename=str(doc.get("filename", "Unknown")),
            file_type=str(doc.get("file_type", "")),
            file_size=int(doc.get("file_size", 0)),
            file_size_readable=str(
                doc.get("file_size_readable", "0 Bytes")
            ),
            chunks_created=int(doc.get("chunks_created", 0)),
            indexed_chunks=doc.get("indexed_chunks"),
            indexing_status=doc.get("indexing_status"),
            uploaded_at=str(doc.get("uploaded_at", "")),
            status=str(doc.get("status", "Processed")),
        )
        for doc in documents
    ]

def delete_document(document_id: str) -> dict:
    _ensure_directories()

    documents = _load_json(DOCUMENTS_FILE, [])
    chunks = _load_json(CHUNKS_FILE, [])

    document = next(
    (
        doc for doc in documents
        if doc.get("id") == document_id or doc.get("filename") == document_id
    ),
    None,
    )

    if document is None:
        raise DocumentProcessingError(
            message="Document not found.",
            details=f"No document found with id '{document_id}'.",
            status_code=404,
        )

    filename = document["filename"]

    updated_documents = [
    doc for doc in documents
    if doc.get("id") != document_id and doc.get("filename") != document_id
    ]

    document_chunks = [
    chunk for chunk in chunks
    if chunk.get("document_id") == document_id or chunk.get("document_name") == filename
    ]

    updated_chunks = [
    chunk for chunk in chunks
    if chunk.get("document_id") != document_id and chunk.get("document_name") != filename
    ]

    _save_json(DOCUMENTS_FILE, updated_documents)
    _save_json(CHUNKS_FILE, updated_chunks)

    file_path = UPLOADS_DIR / filename
    if file_path.exists():
        file_path.unlink(missing_ok=True)

    try:
        settings = get_settings()
        vector_store = VectorStore(persist_directory=settings.CHROMA_PERSIST_DIR)

        vector_ids = [
            f"{document_id}_chunk_{chunk.get('chunk_index')}"
            for chunk in document_chunks
        ]

        if vector_ids:
            vector_store.collection.delete(ids=vector_ids)

    except Exception as exc:
        logger.warning("Vector cleanup failed for %s: %s", filename, exc)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "filename": filename,
    }

def get_document_details(document_id: str) -> dict:
    _ensure_directories()

    documents = _load_json(DOCUMENTS_FILE, [])
    chunks = _load_json(CHUNKS_FILE, [])

    document = next(
        (
            doc for doc in documents
            if doc.get("id") == document_id or doc.get("filename") == document_id
        ),
        None,
    )

    if document is None:
        raise DocumentProcessingError(
            message="Document not found.",
            details=f"No document found with id '{document_id}'.",
            status_code=404,
        )

    filename = document["filename"]
    document_chunks = [
        chunk for chunk in chunks
        if chunk.get("document_id") == document.get("id")
        or chunk.get("document_name") == filename
    ]

    preview_text = "\n\n".join(
        str(chunk.get("text", "")) for chunk in document_chunks[:3]
    )

    return {
        "document": document,
        "chunks": document_chunks,
        "preview": preview_text[:2000],
    }

def get_document_file_path(document_id: str) -> Path:
    _ensure_directories()

    documents = _load_json(DOCUMENTS_FILE, [])

    document = next(
        (
            doc for doc in documents
            if doc.get("id") == document_id or doc.get("filename") == document_id
        ),
        None,
    )

    if document is None:
        raise DocumentProcessingError(
            message="Document not found.",
            details=f"No document found with id '{document_id}'.",
            status_code=404,
        )

    file_path = UPLOADS_DIR / document["filename"]

    if not file_path.exists():
        raise DocumentProcessingError(
            message="File not found.",
            details=f"Uploaded file '{document['filename']}' no longer exists.",
            status_code=404,
        )

    return file_path

def rename_document(document_id: str, new_filename: str) -> dict:
    _ensure_directories()

    documents = _load_json(DOCUMENTS_FILE, [])
    chunks = _load_json(CHUNKS_FILE, [])

    document = next(
        (doc for doc in documents if doc.get("id") == document_id or doc.get("filename") == document_id),
        None,
    )

    if document is None:
        raise DocumentProcessingError("Document not found.", f"No document found with id '{document_id}'.", 404)

    old_filename = document["filename"]
    extension = Path(old_filename).suffix

    if not new_filename.endswith(extension):
        new_filename += extension

    old_path = UPLOADS_DIR / old_filename
    new_path = UPLOADS_DIR / new_filename

    if new_path.exists():
        raise DocumentProcessingError("Filename already exists.", f"{new_filename} already exists.", 400)

    if old_path.exists():
        old_path.rename(new_path)

    document["filename"] = new_filename

    for chunk in chunks:
        if chunk.get("document_id") == document.get("id") or chunk.get("document_name") == old_filename:
            chunk["document_name"] = new_filename

    _save_json(DOCUMENTS_FILE, documents)
    _save_json(CHUNKS_FILE, chunks)

    return {
        "message": "Document renamed successfully.",
        "old_filename": old_filename,
        "new_filename": new_filename,
    }


def search_documents(query: str) -> list[DocumentSummary]:
    documents = list_documents()

    if not query or not query.strip():
        return documents

    q = query.lower().strip()

    return [
        doc for doc in documents
        if q in doc.filename.lower()
        or q in doc.file_type.lower()
        or q in doc.status.lower()
        or q in doc.uploaded_at.lower()
    ]

async def process_upload(file: UploadFile) -> DocumentSummary:
    _ensure_directories()

    filename = file.filename
    logger.info("File received: %s", filename or "<no filename>")

    try:
        filename, file_type = _validate_file(filename)
    except DocumentProcessingError:
        raise

    contents = await file.read()
    if not contents:
        raise DocumentProcessingError(
            message="Uploaded file is empty.",
            details="The uploaded file contains no data.",
        )

    file_path = UPLOADS_DIR / filename
    file_path.write_bytes(contents)
    logger.info("File saved: %s (%d bytes)", file_path.name, len(contents))

    try:
        text = _extract_text(file_path, file_type).strip()
    except DocumentProcessingError:
        _cleanup_upload(file_path)
        raise
    except Exception as exc:
        _cleanup_upload(file_path)
        logger.exception("Unexpected extraction error for %s", filename)
        raise DocumentProcessingError(
            message="Unable to process document.",
            details=str(exc),
        ) from exc

    if not text:
        _cleanup_upload(file_path)
        raise DocumentProcessingError(
            message="The uploaded document contains no readable text.",
            details="Text extraction returned an empty result.",
        )

    chunks = chunk_text(text)
    logger.info("Chunks created for %s: %d", filename, len(chunks))

    if not chunks:
        _cleanup_upload(file_path)
        raise DocumentProcessingError(
            message="The uploaded document contains no readable text.",
            details="Chunking produced no valid text chunks.",
        )

    _remove_existing_document(filename)

    uploaded_at_dt = now_utc()
    document_id = generate_document_id()
    file_size = len(contents)

    metadata = DocumentMetadata(
        id=document_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        file_size_readable=format_file_size(file_size),
        chunks_created=len(chunks),
        uploaded_at=format_uploaded_at(uploaded_at_dt),
        status="Processed",
    )

    documents = _load_json(DOCUMENTS_FILE, [])
    documents.append(metadata.model_dump())
    _save_json(DOCUMENTS_FILE, documents)

    chunk_records = [
        ChunkRecord(
            document_id=document_id,
            document_name=filename,
            chunk_index=index,
            content=content,
            created_at=format_uploaded_at(uploaded_at_dt),
        ).model_dump()
        for index, content in enumerate(chunks)
    ]

    all_chunks = _load_json(CHUNKS_FILE, [])
    all_chunks.extend(chunk_records)
    _save_json(CHUNKS_FILE, all_chunks)

    indexed_chunks, indexing_status = _index_chunks_in_vector_store(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        chunks=chunks,
        upload_time=format_uploaded_at(uploaded_at_dt),
    )

    if indexing_status == "indexing_failed":
        logger.warning(
            "Document uploaded and chunked, but vector indexing failed for %s",
            metadata.filename,
        )

    logger.info(
        "Upload complete: %s, type=%s, chunks=%d, indexed=%d, status=%s",
        metadata.filename,
        metadata.file_type,
        metadata.chunks_created,
        indexed_chunks,
        indexing_status,
    )

    return DocumentSummary(
        id=metadata.id,
        filename=metadata.filename,
        file_type=metadata.file_type,
        file_size=metadata.file_size,
        file_size_readable=metadata.file_size_readable,
        chunks_created=metadata.chunks_created,
        indexed_chunks=indexed_chunks,
        indexing_status=indexing_status,
        uploaded_at=metadata.uploaded_at,
        status=metadata.status,
    )
