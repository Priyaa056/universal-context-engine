from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    file_size_readable: str
    chunks_created: int
    uploaded_at: str
    status: str = "Processed"


class DocumentSummary(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    file_size_readable: str
    chunks_created: int
    uploaded_at: str
    status: str


class UploadSuccessResponse(BaseModel):
    status: str = "success"
    message: str = "Document uploaded and processed successfully"
    document: DocumentSummary


class DocumentsListResponse(BaseModel):
    documents: list[DocumentSummary]


class ChunkRecord(BaseModel):
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    created_at: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: str


# ---------------------------------------------------------------------------
# Phase 3 — Module 2: Semantic Search
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    """Request body for POST /kb/search."""
    query: str
    n_results: int = 5


class SearchResult(BaseModel):
    """A single result returned from a semantic search."""
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    score: float  # similarity score in [0, 1], higher = more relevant


class SearchResponse(BaseModel):
    """Response from POST /kb/search."""
    query: str
    results: list[SearchResult]
    total: int
