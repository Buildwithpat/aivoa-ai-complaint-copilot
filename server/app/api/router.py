from fastapi import APIRouter

from app.api import chat, complaints, documents

api_router = APIRouter(prefix="/api")
api_router.include_router(complaints.router)
api_router.include_router(chat.router)
api_router.include_router(documents.router)
