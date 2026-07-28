from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageRead, ChatSendRequest, ChatSendResponse
from app.services.ai_service import AIService

_FALLBACK_REPLY = "I've updated the complaint based on your message."


class ChatService:
    def __init__(self, db: Session, ai_service: AIService) -> None:
        self.db = db
        self.ai_service = ai_service

    def list_messages(self, complaint_id: str | None) -> list[ChatMessage]:
        query = self.db.query(ChatMessage)
        if complaint_id:
            query = query.filter(ChatMessage.complaint_id == complaint_id)
        return query.order_by(ChatMessage.created_at.asc()).all()

    def _save(self, complaint_id: str | None, role: str, content: str) -> ChatMessage:
        message = ChatMessage(complaint_id=complaint_id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def send(self, payload: ChatSendRequest) -> ChatSendResponse:
        ai_response = self.ai_service.process(
            source="chat",
            input_text=payload.content,
            complaint_id=payload.complaint_id,
        )
        complaint_id = ai_response.complaint.id

        user_message = self._save(complaint_id, "user", payload.content)
        assistant_message = self._save(complaint_id, "assistant", ai_response.summary or _FALLBACK_REPLY)

        return ChatSendResponse(
            user_message=ChatMessageRead.model_validate(user_message),
            assistant_message=ChatMessageRead.model_validate(assistant_message),
            ai_response=ai_response,
        )
