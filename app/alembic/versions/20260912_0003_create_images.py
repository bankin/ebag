"""create images table; link products to images

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("internal_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("internal_name", name="uq_image_internal_name"),
    )

    op.add_column(
        "products",
        sa.Column(
            "image_id",
            sa.Integer(),
            sa.ForeignKey("images.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.drop_column("products", "image_url")


def downgrade() -> None:
    op.add_column(
        "products", sa.Column("image_url", sa.String(length=500), nullable=True)
    )
    op.drop_column("products", "image_id")
    op.drop_table("images")
