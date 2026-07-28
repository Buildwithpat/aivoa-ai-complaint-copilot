"""Plain-text extraction for uploaded complaint documents.

Each extractor takes raw file bytes and returns plain text. Failures in the
underlying parser (corrupt/encrypted PDF, malformed DOCX, ...) are caught and
surfaced as `ExtractionError` so the API layer can return a clean 422 instead
of a raw 500.
"""

import email
from email import policy
from email.message import Message
from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.utils.exceptions import ExtractionError


def _extract_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def _eml_body(message: Message) -> str:
    if not message.is_multipart():
        return str(message.get_content())

    parts = [
        str(part.get_content())
        for part in message.walk()
        if part.get_content_type() == "text/plain" and not part.get_filename()
    ]
    return "\n\n".join(parts)


def _extract_eml(content: bytes) -> str:
    message = email.message_from_bytes(content, policy=policy.default)
    subject = message.get("Subject", "")
    body = _eml_body(message)
    return f"Subject: {subject}\n\n{body}" if subject else body


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(content: bytes) -> str:
    document = DocxDocument(BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


_EXTRACTORS = {
    ".txt": _extract_txt,
    ".eml": _extract_eml,
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
}


def extract_text(content: bytes, extension: str) -> str:
    """Extracts plain text from `content` based on its file `extension`.

    Raises `ExtractionError` if the extension has no extractor, the file
    can't be parsed, or parsing yields no usable text (e.g. a scanned/
    image-only PDF with no text layer).
    """
    extractor = _EXTRACTORS.get(extension)
    if extractor is None:
        raise ExtractionError(f"No text extractor available for '{extension}' files")

    try:
        text = extractor(content).strip()
    except Exception as exc:
        raise ExtractionError(f"Could not read this '{extension}' file — it may be corrupt or unsupported") from exc

    if not text:
        raise ExtractionError("No readable text was found in this document")

    return text
