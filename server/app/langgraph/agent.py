from typing import Any

from langgraph.graph import END, StateGraph

from app.langgraph.nodes import (
    assess_risk,
    check_completeness,
    determine_workflow,
    extract_complaint,
    generate_summary,
    merge_complaint,
    recommend_capa,
    recommend_root_cause,
    validate_response,
)
from app.langgraph.state import ComplaintState


def _route_by_intent(state: ComplaintState) -> str:
    return state.get("intent", "log_complaint")


def build_complaint_agent():
    """Determine Workflow -> Branch (log_complaint / edit_complaint /
    document_extraction, chosen by endpoint — never by an LLM) -> Complaint
    Extraction -> Complaint Update/Merge -> Risk Assessment -> Complaint
    Summary -> Root Cause Recommendation -> CAPA Recommendation ->
    Completeness Checking -> Final JSON Validation -> End.

    All three intents converge on `extract_complaint` — the branch only
    changes which prompt gets built (see app/prompts/complaint_prompts.py)
    — so the graph stays a single linear pipeline downstream of the branch.
    """
    graph = StateGraph(ComplaintState)

    graph.add_node("determine_workflow", determine_workflow)
    graph.add_node("extract_complaint", extract_complaint)
    graph.add_node("merge_complaint", merge_complaint)
    graph.add_node("assess_risk", assess_risk)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("recommend_root_cause", recommend_root_cause)
    graph.add_node("recommend_capa", recommend_capa)
    graph.add_node("check_completeness", check_completeness)
    graph.add_node("validate_response", validate_response)

    graph.set_entry_point("determine_workflow")
    graph.add_conditional_edges(
        "determine_workflow",
        _route_by_intent,
        {
            "log_complaint": "extract_complaint",
            "edit_complaint": "extract_complaint",
            "document_extraction": "extract_complaint",
        },
    )
    graph.add_edge("extract_complaint", "merge_complaint")
    graph.add_edge("merge_complaint", "assess_risk")
    graph.add_edge("assess_risk", "generate_summary")
    graph.add_edge("generate_summary", "recommend_root_cause")
    graph.add_edge("recommend_root_cause", "recommend_capa")
    graph.add_edge("recommend_capa", "check_completeness")
    graph.add_edge("check_completeness", "validate_response")
    graph.add_edge("validate_response", END)

    return graph.compile()


_complaint_agent = build_complaint_agent()


def run_complaint_graph(
    source: str,
    input_text: str,
    current_complaint: dict[str, Any],
    has_existing_complaint: bool = False,
) -> dict[str, Any]:
    """Runs the compiled agent and returns the final structured JSON
    contract dict (complaint / risk_assessment / summary / completeness /
    root_cause / capa / duplicate_probability)."""
    final_state = _complaint_agent.invoke(
        {
            "source": source,
            "input_text": input_text,
            "current_complaint": current_complaint,
            "has_existing_complaint": has_existing_complaint,
        }
    )
    return final_state["result"]
