from typing import Any, Literal, TypedDict

Intent = Literal["log_complaint", "edit_complaint", "document_extraction"]
Source = Literal["chat", "document"]


class ComplaintState(TypedDict, total=False):
    """Shared state threaded through the graph in app/langgraph/agent.py.

    `current_complaint` / `merged_complaint` use the same snake_case field
    names as app.schemas.complaint.ComplaintUpdate so the final result can
    be handed straight to the service layer.
    """

    # Inputs — set by the caller (app/services/ai_service.py) based on
    # which endpoint was called; the graph never asks an LLM to decide this.
    source: Source
    input_text: str
    current_complaint: dict[str, Any]
    has_existing_complaint: bool

    # determine_workflow
    intent: Intent

    # extract_complaint
    extracted_fields: dict[str, Any]

    # merge_complaint
    merged_complaint: dict[str, Any]

    # assess_risk
    risk: dict[str, Any]

    # generate_summary / recommend_root_cause / recommend_capa
    summary: str
    root_cause: str
    capa: str

    # check_completeness
    completeness: dict[str, Any]

    # validate_response
    result: dict[str, Any]
