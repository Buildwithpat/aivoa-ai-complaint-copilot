from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel


class DocumentRead(CamelModel):
    id: str
    complaint_id: str | None = None
    filename: str
    content_type: str | None = None
    size_bytes: int
    uploaded_at: datetime


class DocumentExtractRequest(CamelModel):
    """Input for running pre-extracted document text through the AI
    pipeline directly (e.g. manual testing via Swagger), bypassing file
    upload and text extraction."""

    complaint_id: str | None = None
    text: str = Field(min_length=1)
