"""Add issued_at and deactivated_at to nfc_tags"""

from alembic import op
import sqlalchemy as sa


revision = "20260108_000002"
down_revision = "20260103_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nfc_tags",
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
    )
    op.add_column(
        "nfc_tags",
        sa.Column(
            "deactivated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("nfc_tags", "deactivated_at")
    op.drop_column("nfc_tags", "issued_at")
