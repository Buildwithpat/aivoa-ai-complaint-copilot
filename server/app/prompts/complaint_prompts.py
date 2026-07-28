"""Prompts for the extraction stage: turning natural language (chat) or
already-extracted document text into structured pharmaceutical complaint
fields. Field names are snake_case to match app.schemas.complaint directly.
"""

import json
from typing import Any

_FIELD_GUIDE = """
Return ONLY a single JSON object (no prose, no markdown fences) using ONLY
these keys, and only when the information is actually present in the text —
never guess or invent a value:

- customer_name (string): the pharmacy, hospital, or distributor reporting the complaint
- customer_type (string): e.g. "Retail Pharmacy", "Hospital", "Distributor"
- product_name (string): the drug product name, without strength
- strength (string): e.g. "500mg"
- batch_number (string)
- manufacturing_date (string, format YYYY-MM-DD)
- expiry_date (string, format YYYY-MM-DD)
- affected_quantity (integer)
- unit_of_measure (string): e.g. "Capsules", "Tablets", "Vials"
- complaint_type (string): e.g. "Physical / Appearance Defect", "Adverse Event", "Packaging Defect"
- description (string): a clear 1-3 sentence restatement of the complaint
- date_reported (string, format YYYY-MM-DD)

Do NOT include severity, priority, or risk fields — those are assessed by a
separate step.
"""

_SYSTEM_PROMPT = (
    "You are the extraction engine inside a pharmaceutical customer complaint "
    "intake system. You read complaint text and output ONLY a JSON object — "
    "never prose, never markdown, never an explanation.\n" + _FIELD_GUIDE
)


def build_extraction_prompt(intent: str, input_text: str, current_complaint: dict[str, Any]) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the given intent.

    - log_complaint: a brand new complaint described in natural language.
    - edit_complaint: a natural-language instruction that should change only
      some fields of an existing complaint — the current complaint is
      included so the model has context, but it must only return fields
      that actually changed.
    - document_extraction: plain text already extracted from an uploaded
      document (no OCR happens here — the caller supplies the text).
    """
    if intent == "edit_complaint":
        user = (
            "CURRENT COMPLAINT (JSON):\n"
            f"{json.dumps(current_complaint, default=str)}\n\n"
            "EDIT INSTRUCTION FROM THE USER:\n"
            f"{input_text}\n\n"
            "Return a JSON object containing ONLY the fields that should "
            "CHANGE based on the edit instruction above. Do not include "
            "fields that are unchanged, and do not repeat the current "
            "complaint back."
        )
    elif intent == "document_extraction":
        user = (
            "The following text was extracted from an uploaded complaint "
            "document. Extract the complaint fields from it.\n\n"
            f"DOCUMENT TEXT:\n{input_text}"
        )
    else:
        user = f"COMPLAINT TEXT FROM USER:\n{input_text}"

    return _SYSTEM_PROMPT, user
