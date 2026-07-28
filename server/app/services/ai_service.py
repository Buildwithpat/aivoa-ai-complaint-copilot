from sqlalchemy.orm import Session

from app.langgraph.agent import run_complaint_graph
from app.schemas.complaint import AIComplaintResponse
from app.services.complaint_service import ComplaintService


class AIService:
    """Single integration point between the LangGraph pipeline and the API
    layer: loads the current complaint (if any), runs the graph, persists
    the result, and hands back the project's structured JSON contract. Used
    by both the chat endpoint and the document-extraction endpoint."""

    def __init__(self, db: Session, complaint_service: ComplaintService) -> None:
        self.db = db
        self.complaint_service = complaint_service

    def process(self, source: str, input_text: str, complaint_id: str | None) -> AIComplaintResponse:
        current = self.complaint_service.get_optional(complaint_id) if complaint_id else None
        current_state = ComplaintService.to_state_dict(current)

        result = run_complaint_graph(
            source=source,
            input_text=input_text,
            current_complaint=current_state,
            has_existing_complaint=current is not None,
        )

        # Only target complaint_id for an update if it actually resolved to
        # a row above — a stale/unknown id falls back to creating a new
        # complaint instead of 404ing the whole chat/extraction request.
        target_id = current.id if current is not None else None
        complaint = self.complaint_service.apply_ai_result(target_id, result)
        return self.complaint_service.to_ai_response(complaint)
