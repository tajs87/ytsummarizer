"""Add guest session ownership model

Revision ID: 005
Revises: 004
Create Date: 2026-05-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create guest sessions table and add guest ownership to videos."""
    op.create_table(
        "guest_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("migrated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guest_sessions_id"), "guest_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_guest_sessions_token_hash"), "guest_sessions", ["token_hash"], unique=True
    )

    op.add_column("videos", sa.Column("owner_guest_session_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_videos_owner_guest_session_id_guest_sessions",
        "videos",
        "guest_sessions",
        ["owner_guest_session_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_videos_owner_guest_session_id"), "videos", ["owner_guest_session_id"], unique=False
    )

    op.alter_column("videos", "user_id", existing_type=sa.Integer(), nullable=True)

    op.drop_index(op.f("ix_videos_url_hash"), table_name="videos")
    op.create_index(op.f("ix_videos_url_hash"), "videos", ["url_hash"], unique=False)


def downgrade() -> None:
    """Rollback guest session ownership changes."""
    op.drop_index(op.f("ix_videos_url_hash"), table_name="videos")
    op.create_index(op.f("ix_videos_url_hash"), "videos", ["url_hash"], unique=True)

    op.alter_column("videos", "user_id", existing_type=sa.Integer(), nullable=False)

    op.drop_index(op.f("ix_videos_owner_guest_session_id"), table_name="videos")
    op.drop_constraint(
        "fk_videos_owner_guest_session_id_guest_sessions", "videos", type_="foreignkey"
    )
    op.drop_column("videos", "owner_guest_session_id")

    op.drop_index(op.f("ix_guest_sessions_token_hash"), table_name="guest_sessions")
    op.drop_index(op.f("ix_guest_sessions_id"), table_name="guest_sessions")
    op.drop_table("guest_sessions")
