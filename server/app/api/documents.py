from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.api.deps import get_ai_service, get_document_service
from app.config import settings
from app.schemas.complaint import AIComplaintResponse
from app.schemas.document import DocumentExtractRequest, DocumentRead
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
from app.utils.exceptions import PayloadTooLargeError, UnsupportedFileTypeError

router = APIRouter(prefix="/documents", tags=["documents"])


def _extension_of(filename: str) -> str:
    return f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""


@router.post("/upload", response_model=AIComplaintResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    complaint_id: str | None = Form(None),
    document_service: DocumentService = Depends(get_document_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AIComplaintResponse:
    """Accepts a complaint document (PDF/DOCX/TXT/EML), extracts its text,
    and runs that text through the same LangGraph pipeline as
    `/documents/extract` (source="document") — one round trip from raw file
    to a populated complaint. Document metadata is stored either way."""
    extension = _extension_of(file.filename or "")
    if extension not in settings.allowed_upload_extensions_list:
        raise UnsupportedFileTypeError(
            f"'{extension or 'unknown'}' is not a supported file type. "
            f"Allowed types: {', '.join(settings.allowed_upload_extensions_list)}"
        )

    contents = await file.read()
    size_bytes = len(contents)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise PayloadTooLargeError(f"File exceeds the {settings.max_upload_size_mb}MB upload limit")

    text = document_service.extract_text(contents, extension)
    ai_response = ai_service.process(source="document", input_text=text, complaint_id=complaint_id)

    document_service.save_metadata(
        complaint_id=ai_response.complaint.id,
        filename=file.filename or "unnamed",
        content_type=file.content_type,
        size_bytes=size_bytes,
    )
    return ai_response


@router.get("", response_model=list[DocumentRead])
def list_documents(
    complaint_id: str | None = Query(None, alias="complaintId"),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentRead]:
    return [DocumentRead.model_validate(document) for document in service.list(complaint_id)]


@router.post("/extract", response_model=AIComplaintResponse)
def extract_document(
    payload: DocumentExtractRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> AIComplaintResponse:
    """Runs pre-extracted document text through the same LangGraph pipeline
    as `/documents/upload` and chat (source="document"). Useful for testing
    the AI pipeline directly with arbitrary text, bypassing file upload."""
    return ai_service.process(source="document", input_text=payload.text, complaint_id=payload.complaint_id)
