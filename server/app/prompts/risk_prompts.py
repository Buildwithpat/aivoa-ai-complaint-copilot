"""Prompts for the assessment-stage nodes: risk assessment, summary, root
cause, and CAPA — each a focused, single-purpose call over the merged
complaint fields (see app/langgraph/nodes.py).
"""

import json
from typing import Any


def _complaint_block(complaint: dict[str, Any]) -> str:
    return f"COMPLAINT (JSON):\n{json.dumps(complaint, default=str)}"


def build_risk_prompt(complaint: dict[str, Any]) -> tuple[str, str]:
    system = (
        "You are the risk-classification engine inside a pharmaceutical "
        "customer complaint intake system. Output ONLY a JSON object — "
        "never prose, never markdown — with EXACTLY this shape:\n"
        "{\n"
        '  "severity": "Critical" | "Major" | "Minor",\n'
        '  "priority": "Urgent" | "High" | "Medium" | "Low",\n'
        '  "risk_level": "High" | "Medium" | "Low",\n'
        '  "rationale": string\n'
        "}\n"
        "Base your classification only on the complaint data given — never "
        "invent facts not present in it."
    )
    return system, _complaint_block(complaint)


def build_summary_prompt(complaint: dict[str, Any]) -> tuple[str, str]:
    system = (
        "You are the summarization engine inside a pharmaceutical customer "
        "complaint intake system. Output ONLY a JSON object of the form "
        '{"summary": string} — never prose, never markdown. The summary '
        "must be 1-3 plain-English sentences suitable for a QA reviewer, "
        "based only on the complaint data given."
    )
    return system, _complaint_block(complaint)


def build_root_cause_prompt(complaint: dict[str, Any]) -> tuple[str, str]:
    system = (
        "You are the root-cause analysis engine inside a pharmaceutical "
        "customer complaint intake system. Output ONLY a JSON object of "
        'the form {"root_cause": string} — never prose, never markdown. '
        "Give a preliminary root-cause hypothesis based only on the "
        "complaint data given, noting it is preliminary if the data is "
        "insufficient to be conclusive."
    )
    return system, _complaint_block(complaint)


def build_capa_prompt(complaint: dict[str, Any], root_cause: str) -> tuple[str, str]:
    system = (
        "You are the CAPA (Corrective and Preventive Action) recommendation "
        "engine inside a pharmaceutical customer complaint intake system. "
        'Output ONLY a JSON object of the form {"capa": string} — never '
        "prose, never markdown. Recommend one concrete corrective/preventive "
        "action, consistent with the root-cause hypothesis given."
    )
    user = f"{_complaint_block(complaint)}\n\nROOT CAUSE HYPOTHESIS:\n{root_cause}"
    return system, user
