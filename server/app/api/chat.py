from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_chat_service
from app.schemas.chat import ChatMessageRead, ChatSendRequest, ChatSendResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=list[ChatMessageRead])
def list_messages(
    complaint_id: str | None = Query(None, alias="complaintId"),
    service: ChatService = Depends(get_chat_service),
) -> list[ChatMessageRead]:
    return [ChatMessageRead.model_validate(message) for message in service.list_messages(complaint_id)]


@router.post("/messages", response_model=ChatSendResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: ChatSendRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatSendResponse:
    return service.send(payload)
