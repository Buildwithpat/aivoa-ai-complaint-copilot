from typing import Any

from app.langgraph.parser import (
    call_llm_json,
    sanitize_complaint_dict,
    sanitize_extracted_complaint,
    sanitize_risk,
    sanitize_text_field,
)
from app.langgraph.state import ComplaintState, Intent
from app.prompts.complaint_prompts import build_extraction_prompt
from app.prompts.risk_prompts import build_capa_prompt, build_risk_prompt, build_root_cause_prompt, build_summary_prompt

_REQUIRED_FIELDS: dict[str, str] = {
    "customer_name": "Customer Name",
    "product_name": "Product Name",
    "batch_number": "Batch Number",
    "affected_quantity": "Affected Quantity",
    "description": "Complaint Description",
    "severity": "Severity",
}


def determine_workflow(state: ComplaintState) -> dict[str, Any]:
    """Determine Workflow node: NOT an LLM call. Which workflow runs is
    decided entirely by which endpoint the caller hit — `source` and
    `has_existing_complaint` are set by app/services/ai_service.py based on
    whether this came from the chat endpoint or the document-extraction
    endpoint, and whether a complaint id was resolved."""
    if state.get("source") == "document":
        intent: Intent = "document_extraction"
    elif state.get("has_existing_complaint"):
        intent = "edit_complaint"
    else:
        intent = "log_complaint"

    return {"intent": intent}


def extract_complaint(state: ComplaintState) -> dict[str, Any]:
    """Complaint Extraction node: pulls structured fields out of the raw
    input text (chat message or already-extracted document text)."""
    intent = state.get("intent", "log_complaint")
    current = state.get("current_complaint") or {}

    system_prompt, user_prompt = build_extraction_prompt(intent, state.get("input_text", ""), current)
    raw = call_llm_json(system_prompt, user_prompt)
    extracted = sanitize_extracted_complaint(raw)

    return {"extracted_fields": extracted}


def merge_complaint(state: ComplaintState) -> dict[str, Any]:
    """Complaint Update/Merge node: pure logic, no LLM call. Overlays the
    newly extracted fields on top of the current complaint so editing a
    complaint only changes what the user actually mentioned, preserving
    everything else."""
    current = state.get("current_complaint") or {}
    extracted = state.get("extracted_fields") or {}
    return {"merged_complaint": {**current, **extracted}}


def assess_risk(state: ComplaintState) -> dict[str, Any]:
    """Risk Assessment node: severity, priority, and risk classification."""
    complaint = state.get("merged_complaint") or {}
    system_prompt, user_prompt = build_risk_prompt(complaint)
    risk = sanitize_risk(call_llm_json(system_prompt, user_prompt))

    updated_complaint = {**complaint, "severity": risk["severity"], "priority": risk["priority"]}
    return {"merged_complaint": updated_complaint, "risk": risk}


def generate_summary(state: ComplaintState) -> dict[str, Any]:
    """Complaint Summary node."""
    complaint = state.get("merged_complaint") or {}
    system_prompt, user_prompt = build_summary_prompt(complaint)
    summary = sanitize_text_field(call_llm_json(system_prompt, user_prompt), "summary")
    return {"summary": summary}


def recommend_root_cause(state: ComplaintState) -> dict[str, Any]:
    """Root Cause Recommendation node."""
    complaint = state.get("merged_complaint") or {}
    system_prompt, user_prompt = build_root_cause_prompt(complaint)
    root_cause = sanitize_text_field(call_llm_json(system_prompt, user_prompt), "root_cause")
    return {"root_cause": root_cause}


def recommend_capa(state: ComplaintState) -> dict[str, Any]:
    """CAPA Recommendation node."""
    complaint = state.get("merged_complaint") or {}
    root_cause = state.get("root_cause", "")
    system_prompt, user_prompt = build_capa_prompt(complaint, root_cause)
    capa = sanitize_text_field(call_llm_json(system_prompt, user_prompt), "capa")
    return {"capa": capa}


def check_completeness(state: ComplaintState) -> dict[str, Any]:
    """Completeness Checking node: pure logic, no LLM call — whether a
    complaint is missing a required field is a factual check, not a
    judgment call, so a deterministic rule is faster and more reliable
    than an LLM guess here."""
    complaint = state.get("merged_complaint") or {}
    missing = [label for field, label in _REQUIRED_FIELDS.items() if not complaint.get(field)]
    return {"completeness": {"is_complete": not missing, "missing_fields": missing}}


def validate_response(state: ComplaintState) -> dict[str, Any]:
    """Final JSON Validation node: re-validates the assembled complaint
    fields against the same whitelist/type rules as extraction, and
    guarantees every top-level key the project's JSON contract requires is
    present with the right type — regardless of what upstream nodes
    produced."""
    complaint = sanitize_complaint_dict(state.get("merged_complaint") or {})
    risk = state.get("risk") or {}
    completeness = state.get("completeness") or {}

    result = {
        "complaint": complaint,
        "risk_assessment": {
            "risk_level": risk.get("risk_level", "Not Assessed"),
            "rationale": risk.get("rationale", ""),
        },
        "summary": state.get("summary", ""),
        "completeness": {
            "is_complete": completeness.get("is_complete"),
            "missing_fields": completeness.get("missing_fields", []),
        },
        "root_cause": state.get("root_cause", ""),
        "capa": state.get("capa", ""),
        "duplicate_probability": 0.0,
    }
    return {"result": result}
