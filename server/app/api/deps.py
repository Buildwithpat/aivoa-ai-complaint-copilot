from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.ai_service import AIService
from app.services.chat_service import ChatService
from app.services.complaint_service import ComplaintService
from app.services.document_service import DocumentService


def get_complaint_service(db: Session = Depends(get_db)) -> ComplaintService:
    return ComplaintService(db)


def get_ai_service(
    db: Session = Depends(get_db),
    complaint_service: ComplaintService = Depends(get_complaint_service),
) -> AIService:
    return AIService(db, complaint_service)


def get_chat_service(
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> ChatService:
    return ChatService(db, ai_service)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)
