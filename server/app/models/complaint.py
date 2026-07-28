from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Complaint(Base):
    """A pharmaceutical customer complaint plus the AI-generated assessment
    fields, denormalized onto the same row since each complaint has exactly
    one current assessment (see PROJECT_CONTEXT.md JSON contract)."""

    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    # Core complaint fields
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(50), nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    affected_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_of_measure: Mapped[str | None] = mapped_column(String(50), nullable=True)
    complaint_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_reported: Mapped[date | None] = mapped_column(Date, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Draft", server_default="Draft")
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-generated assessment fields, populated by the LangGraph pipeline.
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    risk_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa: Mapped[str | None] = mapped_column(Text, nullable=True)
    duplicate_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    is_complete: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    missing_fields: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
