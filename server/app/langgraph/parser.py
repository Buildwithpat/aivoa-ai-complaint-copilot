"""Parsing, retry, and validation for raw LLM output.

Nothing the model returns is trusted as-is: `call_llm_json` retries on
invalid/empty JSON before falling back, and the `sanitize_*` functions
coerce every field to an expected type/enum (or drop it) before it is ever
merged into complaint state, persisted, or returned to the client.
"""

import json
import logging
import re
from typing import Any

from app.services.groq_client import chat_completion_json

logger = logging.getLogger("aivoa.langgraph")

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_SEVERITY = {"Critical", "Major", "Minor", "Not Assessed"}
ALLOWED_PRIORITY = {"Urgent", "High", "Medium", "Low", "Not Assessed"}
ALLOWED_RISK_LEVEL = {"High", "Medium", "Low", "Not Assessed"}

_EXTRACTION_STRING_FIELDS = (
    "customer_name",
    "customer_type",
    "product_name",
    "strength",
    "batch_number",
    "unit_of_measure",
    "complaint_type",
    "description",
)
_EXTRACTION_DATE_FIELDS = ("manufacturing_date", "expiry_date", "date_reported")


def parse_json_response(raw: str) -> dict[str, Any]:
    """Best-effort extraction of a JSON object from an LLM response,
    tolerant of markdown fences or stray prose around the JSON."""
    if not raw:
        return {}

    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}

    return parsed if isinstance(parsed, dict) else {}


def call_llm_json(system_prompt: str, user_prompt: str, retries: int = 1) -> dict[str, Any]:
    """Calls Groq and parses the response as JSON, retrying on failure
    (network error, empty response, unparsable JSON) up to `retries` extra
    times before gracefully falling back to an empty dict — callers always
    get a dict back and apply their own sanitize_* defaults on top."""
    for attempt in range(retries + 1):
        try:
            raw = chat_completion_json(system_prompt, user_prompt)
        except Exception:
            logger.warning("Groq call failed (attempt %s/%s)", attempt + 1, retries + 1, exc_info=True)
            continue

        parsed = parse_json_response(raw)
        if parsed:
            return parsed
        logger.warning("Groq response was not valid JSON (attempt %s/%s)", attempt + 1, retries + 1)

    return {}


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return None


def _clean_date(value: Any) -> str | None:
    text = _clean_str(value)
    if text and _ISO_DATE_RE.match(text):
        return text
    return None


def _clean_enum(value: Any, allowed: set[str]) -> str | None:
    text = _clean_str(value)
    if not text:
        return None
    for option in allowed:
        if option.lower() == text.lower():
            return option
    return None


def _clean_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.strip().lower() in ("true", "yes", "complete"):
            return True
        if value.strip().lower() in ("false", "no", "incomplete"):
            return False
    return None


def _clean_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if (text := _clean_str(item))]


def sanitize_extracted_complaint(data: dict[str, Any]) -> dict[str, Any]:
    """Validates the extraction node's LLM output. Only known fields with
    valid values survive; anything malformed/unrecognized is dropped."""
    cleaned: dict[str, Any] = {}

    for field in _EXTRACTION_STRING_FIELDS:
        value = _clean_str(data.get(field))
        if value is not None:
            cleaned[field] = value

    quantity = _clean_int(data.get("affected_quantity"))
    if quantity is not None:
        cleaned["affected_quantity"] = quantity

    for field in _EXTRACTION_DATE_FIELDS:
        value = _clean_date(data.get(field))
        if value is not None:
            cleaned[field] = value

    return cleaned


def sanitize_risk(data: dict[str, Any]) -> dict[str, Any]:
    """Validates the risk-assessment node's LLM output."""
    return {
        "severity": _clean_enum(data.get("severity"), ALLOWED_SEVERITY) or "Not Assessed",
        "priority": _clean_enum(data.get("priority"), ALLOWED_PRIORITY) or "Not Assessed",
        "risk_level": _clean_enum(data.get("risk_level"), ALLOWED_RISK_LEVEL) or "Not Assessed",
        "rationale": _clean_str(data.get("rationale")) or "",
    }


def sanitize_text_field(data: dict[str, Any], key: str) -> str:
    """Validates a single free-text field (summary / root_cause / capa /
    next_action) from a node's LLM output."""
    return _clean_str(data.get(key)) or ""


def sanitize_complaint_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Final-validation pass for the assembled `complaint` sub-object,
    reusing the same field whitelist/coercion rules as extraction so
    nothing malformed survives into the response (see validate_response
    node in app/langgraph/nodes.py)."""
    cleaned = sanitize_extracted_complaint(data)

    severity = _clean_enum(data.get("severity"), ALLOWED_SEVERITY)
    if severity:
        cleaned["severity"] = severity
    priority = _clean_enum(data.get("priority"), ALLOWED_PRIORITY)
    if priority:
        cleaned["priority"] = priority
    next_action = _clean_str(data.get("next_action"))
    if next_action:
        cleaned["next_action"] = next_action
    status = _clean_str(data.get("status"))
    if status:
        cleaned["status"] = status

    return cleaned
