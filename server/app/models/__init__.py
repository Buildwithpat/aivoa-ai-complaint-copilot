# Import every model so Base.metadata / Alembic autogenerate can see them.
from app.models.chat_message import ChatMessage
from app.models.complaint import Complaint
from app.models.document import Document

__all__ = ["Complaint", "ChatMessage", "Document"]
