"""Add ownership indexes for guest migration queries

Revision ID: 006
Revises: 005
Create Date: 2026-05-22

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add query-oriented indexes for guest and user ownership paths."""
    op.create_index(
        "ix_videos_owner_user_created_at",
        "videos",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_videos_owner_guest_created_at",
        "videos",
        ["owner_guest_session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop ownership indexes."""
    op.drop_index("ix_videos_owner_guest_created_at", table_name="videos")
    op.drop_index("ix_videos_owner_user_created_at", table_name="videos")
