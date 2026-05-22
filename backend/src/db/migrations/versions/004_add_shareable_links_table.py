"""Add shareable links table

Revision ID: 004
Revises: 003
Create Date: 2026-05-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: str | None = '003'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create shareable_links table."""
    op.create_table(
        'shareable_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shareable_links_id'), 'shareable_links', ['id'], unique=False)
    op.create_index(op.f('ix_shareable_links_video_id'), 'shareable_links', ['video_id'], unique=False)
    op.create_index(op.f('ix_shareable_links_user_id'), 'shareable_links', ['user_id'], unique=False)
    op.create_index(op.f('ix_shareable_links_token'), 'shareable_links', ['token'], unique=True)


def downgrade() -> None:
    """Drop shareable_links table."""
    op.drop_index(op.f('ix_shareable_links_token'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_user_id'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_video_id'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_id'), table_name='shareable_links')
    op.drop_table('shareable_links')
