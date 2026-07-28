from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelModel
from app.schemas.complaint import AIComplaintResponse
from app.schemas.enums import ChatRole


class ChatMessageRead(CamelModel):
    id: str
    complaint_id: str | None = None
    role: ChatRole
    content: str
    created_at: datetime


class ChatSendRequest(CamelModel):
    complaint_id: str | None = None
    content: str = Field(min_length=1, max_length=4000)


class ChatSendResponse(CamelModel):
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
    ai_response: AIComplaintResponse
