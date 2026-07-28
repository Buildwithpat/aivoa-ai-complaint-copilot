from sqlalchemy.orm import Session

from app.models.document import Document
from app.utils.text_extraction import extract_text


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def extract_text(self, content: bytes, extension: str) -> str:
        """Extracts plain text from an uploaded file's raw bytes. Raises
        `ExtractionError` (see app/utils/text_extraction.py) on failure."""
        return extract_text(content, extension)

    def save_metadata(
        self,
        complaint_id: str | None,
        filename: str,
        content_type: str | None,
        size_bytes: int,
    ) -> Document:
        document = Document(
            complaint_id=complaint_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list(self, complaint_id: str | None) -> list[Document]:
        query = self.db.query(Document)
        if complaint_id:
            query = query.filter(Document.complaint_id == complaint_id)
        return query.order_by(Document.uploaded_at.desc()).all()
