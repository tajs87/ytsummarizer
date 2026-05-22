"""Add summary and highlight tables

Revision ID: 003
Revises: 002
Create Date: 2026-05-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create summaries and highlights tables."""
    # Create enum once; avoid duplicate CREATE TYPE during table creation.
    summary_type_enum = postgresql.ENUM(
        "BRIEF", "DETAILED", "BULLET_POINTS", name="summarytype", create_type=False
    )
    summary_type_enum.create(op.get_bind(), checkfirst=True)

    # Create summaries table
    op.create_table(
        "summaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("summary_type", summary_type_enum, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_summaries_id"), "summaries", ["id"], unique=False)
    op.create_index(op.f("ix_summaries_video_id"), "summaries", ["video_id"], unique=False)

    # Create highlights table
    op.create_table(
        "highlights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("summary_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["summary_id"], ["summaries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_highlights_id"), "highlights", ["id"], unique=False)
    op.create_index(op.f("ix_highlights_summary_id"), "highlights", ["summary_id"], unique=False)


def downgrade() -> None:
    """Drop highlights and summaries tables."""
    op.drop_index(op.f("ix_highlights_summary_id"), table_name="highlights")
    op.drop_index(op.f("ix_highlights_id"), table_name="highlights")
    op.drop_table("highlights")

    op.drop_index(op.f("ix_summaries_video_id"), table_name="summaries")
    op.drop_index(op.f("ix_summaries_id"), table_name="summaries")
    op.drop_table("summaries")

    # Drop enum
    op.execute("DROP TYPE IF EXISTS summarytype")
