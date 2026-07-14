from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from services.document_service import (
    DocumentProcessingError,
    delete_document,
    get_document_details,
    get_document_file_path,
    list_documents,
    process_upload,
    rename_document,
)

router = APIRouter(prefix="/api/documents", tags=["Documents"])
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        document = await process_upload(file)

        return {
            "message": "Document uploaded and processed successfully.",
            "document": document,
        }

    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


class RenameRequest(BaseModel):
    filename: str


@router.get("")
def get_documents():
    return {"documents": list_documents()}


@router.get("/search")
def search(q: str = Query(default="")):
    return {"documents": search_documents(q)}


@router.get("/{document_id}")
def get_document(document_id: str):
    try:
        return get_document_details(document_id)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"message": exc.message, "details": exc.details})


@router.get("/{document_id}/download")
def download_document(document_id: str):
    try:
        file_path = get_document_file_path(document_id)
        return FileResponse(path=str(file_path), filename=file_path.name, media_type="application/octet-stream")
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"message": exc.message, "details": exc.details})


@router.patch("/{document_id}")
def rename(document_id: str, payload: RenameRequest):
    try:
        return rename_document(document_id, payload.filename)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"message": exc.message, "details": exc.details})


@router.delete("/{document_id}")
def remove_document(document_id: str):
    try:
        return delete_document(document_id)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"message": exc.message, "details": exc.details})
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))