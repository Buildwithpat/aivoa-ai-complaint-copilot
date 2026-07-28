from datetime import date, datetime

from pydantic import Field

from app.schemas.base import CamelModel
from app.schemas.enums import ComplaintStatus, Priority, RiskLevel, Severity


class ComplaintCreate(CamelModel):
    customer_name: str | None = None
    customer_type: str | None = None
    product_name: str | None = None
    strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    affected_quantity: int | None = Field(default=None, ge=0)
    unit_of_measure: str | None = None
    complaint_type: str | None = None
    description: str | None = None
    date_reported: date | None = None
    severity: Severity | None = None
    priority: Priority | None = None
    status: ComplaintStatus = "Draft"
    next_action: str | None = None


class ComplaintUpdate(CamelModel):
    """All fields optional so callers (manual edits, or the LangGraph
    pipeline) can patch just what changed. Includes the AI-derived fields
    so extraction results can be written back through the same endpoint."""

    customer_name: str | None = None
    customer_type: str | None = None
    product_name: str | None = None
    strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    affected_quantity: int | None = Field(default=None, ge=0)
    unit_of_measure: str | None = None
    complaint_type: str | None = None
    description: str | None = None
    date_reported: date | None = None
    severity: Severity | None = None
    priority: Priority | None = None
    status: ComplaintStatus | None = None
    next_action: str | None = None

    risk_level: RiskLevel | None = None
    risk_rationale: str | None = None
    summary: str | None = None
    root_cause: str | None = None
    capa: str | None = None
    duplicate_probability: float | None = Field(default=None, ge=0, le=1)
    is_complete: bool | None = None
    missing_fields: list[str] | None = None


class ComplaintRead(CamelModel):
    id: str
    customer_name: str | None = None
    customer_type: str | None = None
    product_name: str | None = None
    strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    affected_quantity: int | None = None
    unit_of_measure: str | None = None
    complaint_type: str | None = None
    description: str | None = None
    date_reported: date | None = None
    severity: Severity | None = None
    priority: Priority | None = None
    status: ComplaintStatus
    next_action: str | None = None
    created_at: datetime
    updated_at: datetime


class RiskAssessment(CamelModel):
    risk_level: RiskLevel | None = None
    rationale: str | None = None


class Completeness(CamelModel):
    is_complete: bool | None = None
    missing_fields: list[str] = Field(default_factory=list)


class AIComplaintResponse(CamelModel):
    """Mirrors the fixed JSON contract every AI response must follow, per
    PROJECT_CONTEXT.md — the shape returned by the LangGraph pipeline."""

    complaint: ComplaintRead
    risk_assessment: RiskAssessment
    summary: str = ""
    completeness: Completeness
    root_cause: str = ""
    capa: str = ""
    duplicate_probability: float = 0.0
