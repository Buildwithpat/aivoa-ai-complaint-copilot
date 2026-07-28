from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.schemas.complaint import (
    AIComplaintResponse,
    Completeness,
    ComplaintCreate,
    ComplaintRead,
    ComplaintUpdate,
    RiskAssessment,
)
from app.utils.exceptions import NotFoundError

# Fields fed into the LangGraph state as "current_complaint" and written
# back from its "result.complaint" — kept separate from the AI-only columns
# (risk_level, summary, ...) which are applied directly in apply_ai_result.
_STATE_FIELDS = (
    "customer_name",
    "customer_type",
    "product_name",
    "strength",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "affected_quantity",
    "unit_of_measure",
    "complaint_type",
    "description",
    "date_reported",
    "severity",
    "priority",
    "status",
    "next_action",
)


class ComplaintService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _generate_id(self) -> str:
        """CMP-<year>-<sequence>, e.g. CMP-2026-0001. Sequence is derived by
        counting existing rows for the year — fine for this assignment's
        scale; a DB sequence would be used under real concurrent load."""
        year = datetime.now(UTC).year
        prefix = f"CMP-{year}-"
        count = self.db.query(func.count(Complaint.id)).filter(Complaint.id.like(f"{prefix}%")).scalar() or 0
        return f"{prefix}{count + 1:04d}"

    def create(self, payload: ComplaintCreate) -> Complaint:
        complaint = Complaint(id=self._generate_id(), **payload.model_dump(exclude_unset=True))
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    def get(self, complaint_id: str) -> Complaint:
        complaint = self.db.get(Complaint, complaint_id)
        if complaint is None:
            raise NotFoundError(f"Complaint '{complaint_id}' was not found")
        return complaint

    def get_optional(self, complaint_id: str) -> Complaint | None:
        return self.db.get(Complaint, complaint_id)

    def list(
        self,
        skip: int,
        limit: int,
        status: str | None = None,
        severity: str | None = None,
    ) -> tuple[list[Complaint], int]:
        query = self.db.query(Complaint)
        if status:
            query = query.filter(Complaint.status == status)
        if severity:
            query = query.filter(Complaint.severity == severity)

        total = query.count()
        items = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def update(self, complaint_id: str, payload: ComplaintUpdate) -> Complaint:
        complaint = self.get(complaint_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(complaint, field, value)
        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    @staticmethod
    def to_ai_response(complaint: Complaint) -> AIComplaintResponse:
        return AIComplaintResponse(
            complaint=ComplaintRead.model_validate(complaint),
            risk_assessment=RiskAssessment(risk_level=complaint.risk_level, rationale=complaint.risk_rationale),
            summary=complaint.summary or "",
            completeness=Completeness(
                is_complete=complaint.is_complete, missing_fields=complaint.missing_fields or []
            ),
            root_cause=complaint.root_cause or "",
            capa=complaint.capa or "",
            duplicate_probability=complaint.duplicate_probability or 0.0,
        )

    @staticmethod
    def to_state_dict(complaint: Complaint | None) -> dict[str, Any]:
        """Builds the `current_complaint` dict fed into the LangGraph state
        — only the fields the graph is allowed to read/rewrite, with dates
        as ISO strings so they serialize cleanly into prompts."""
        if complaint is None:
            return {}

        state: dict[str, Any] = {}
        for field in _STATE_FIELDS:
            value = getattr(complaint, field)
            if isinstance(value, date):
                value = value.isoformat()
            if value is not None:
                state[field] = value
        return state

    def apply_ai_result(self, complaint_id: str | None, result: dict[str, Any]) -> Complaint:
        """Persists a LangGraph result (see app/langgraph/agent.py),
        creating a new complaint if `complaint_id` is None, otherwise
        updating the existing one. This is the single place AI output gets
        written to the database."""
        complaint_fields = result.get("complaint") or {}
        risk = result.get("risk_assessment") or {}
        completeness = result.get("completeness") or {}

        update_data: dict[str, Any] = {
            key: value for key, value in complaint_fields.items() if key in ComplaintUpdate.model_fields
        }
        update_data.update(
            risk_level=risk.get("risk_level"),
            risk_rationale=risk.get("rationale"),
            summary=result.get("summary"),
            root_cause=result.get("root_cause"),
            capa=result.get("capa"),
            duplicate_probability=result.get("duplicate_probability"),
            is_complete=completeness.get("is_complete"),
            missing_fields=completeness.get("missing_fields"),
        )
        update_payload = ComplaintUpdate(**update_data)

        if complaint_id:
            return self.update(complaint_id, update_payload)

        create_data = {key: value for key, value in complaint_fields.items() if key in ComplaintCreate.model_fields}
        complaint = self.create(ComplaintCreate(**create_data))
        return self.update(complaint.id, update_payload)
