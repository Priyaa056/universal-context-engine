import json
import logging
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from models.schemas import ChunkRecord, DocumentMetadata, DocumentSummary
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


def list_documents() -> list[DocumentSummary]:
    _ensure_directories()
    documents = _load_json(DOCUMENTS_FILE, [])
    return [
        DocumentSummary(
            id=doc.get("id", doc["filename"]),
            filename=doc["filename"],
            file_type=doc["file_type"],
            file_size=doc.get("file_size", 0),
            file_size_readable=doc.get("file_size_readable", "0 Bytes"),
            chunks_created=doc["chunks_created"],
            uploaded_at=doc.get("uploaded_at", ""),
            status=doc.get("status", "Processed"),
        )
        for doc in documents
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

    logger.info(
        "Upload complete: %s, type=%s, chunks=%d",
        metadata.filename,
        metadata.file_type,
        metadata.chunks_created,
    )

    return DocumentSummary(
        id=metadata.id,
        filename=metadata.filename,
        file_type=metadata.file_type,
        file_size=metadata.file_size,
        file_size_readable=metadata.file_size_readable,
        chunks_created=metadata.chunks_created,
        uploaded_at=metadata.uploaded_at,
        status=metadata.status,
    )
