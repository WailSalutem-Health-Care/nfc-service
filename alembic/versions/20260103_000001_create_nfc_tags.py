"""
Create nfc_tags table

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Initial database migration to create the nfc_tags table.
    Establishes the core table structure for NFC tag management.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260103_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nfc_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tag_id", sa.String(), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("nfc_tags")
