import logging

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from models.schemas import DocumentsListResponse, ErrorResponse, UploadSuccessResponse
from services.document_service import DocumentProcessingError, list_documents, process_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])


@router.post(
    "/upload",
    response_model=UploadSuccessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_document(file: UploadFile = File(...)):
    try:
        document = await process_upload(file)
        return UploadSuccessResponse(document=document)
    except DocumentProcessingError as exc:
        logger.error("Upload failed: %s — %s", exc.message, exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "details": exc.details,
            },
        )
    except Exception as exc:
        logger.exception("Unexpected upload error")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An unexpected error occurred while processing the upload.",
                "details": str(exc),
            },
        )


@router.get("/documents", response_model=DocumentsListResponse)
def get_documents():
    return DocumentsListResponse(documents=list_documents())
