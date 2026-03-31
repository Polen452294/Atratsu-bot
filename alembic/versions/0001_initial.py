"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-04-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_source", sa.String(length=50), nullable=True),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("route_from", sa.String(length=255), nullable=False),
        sa.Column("route_to", sa.String(length=255), nullable=False),
        sa.Column("distance_km", sa.Integer(), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vehicle_type", sa.String(length=100), nullable=False),
        sa.Column("weight_tons", sa.Numeric(10, 2), nullable=False),
        sa.Column("volume_m3", sa.Numeric(10, 2), nullable=True),
        sa.Column("budget_rub", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="created"),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "carrier_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_carrier_id", sa.String(length=100), nullable=True),
        sa.Column("carrier_name", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_nick", sa.String(length=100), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("proposed_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("vehicle_type", sa.String(length=100), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("route_comment", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("is_selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "deals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("carrier_match_id", sa.Integer(), sa.ForeignKey("carrier_matches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="initiated"),
        sa.Column("initiated_message", sa.Text(), nullable=True),
        sa.Column("initiated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "export_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("format", sa.String(length=20), nullable=False, server_default="json"),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("actor", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_carrier_matches_lot_id", "carrier_matches", ["lot_id"])
    op.create_index("ix_deals_lot_id", "deals", ["lot_id"])
    op.create_index("ix_export_files_lot_id", "export_files", ["lot_id"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_index("ix_export_files_lot_id", table_name="export_files")
    op.drop_index("ix_deals_lot_id", table_name="deals")
    op.drop_index("ix_carrier_matches_lot_id", table_name="carrier_matches")

    op.drop_table("audit_logs")
    op.drop_table("export_files")
    op.drop_table("deals")
    op.drop_table("carrier_matches")
    op.drop_table("lots")