"""initial schema: complaints, chat_messages, documents

Revision ID: c92bd216a841
Revises:
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c92bd216a841"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "complaints",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_type", sa.String(length=100), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("strength", sa.String(length=50), nullable=True),
        sa.Column("batch_number", sa.String(length=100), nullable=True),
        sa.Column("manufacturing_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("affected_quantity", sa.Integer(), nullable=True),
        sa.Column("unit_of_measure", sa.String(length=50), nullable=True),
        sa.Column("complaint_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date_reported", sa.Date(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="Draft"),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("risk_rationale", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("capa", sa.Text(), nullable=True),
        sa.Column("duplicate_probability", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_complete", sa.Boolean(), nullable=True),
        sa.Column("missing_fields", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "complaint_id",
            sa.String(length=32),
            sa.ForeignKey("complaints.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("role", sa.String(length=10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_chat_messages_complaint_id", "chat_messages", ["complaint_id"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "complaint_id",
            sa.String(length=32),
            sa.ForeignKey("complaints.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_documents_complaint_id", "documents", ["complaint_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_complaint_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_chat_messages_complaint_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_table("complaints")
