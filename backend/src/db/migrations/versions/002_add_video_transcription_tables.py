"""Add video and transcription tables

Revision ID: 002
Revises: 001
Create Date: 2026-05-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create videos and transcriptions tables."""
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('url_hash', sa.String(length=64), nullable=False),
        sa.Column('platform', sa.Enum('YOUTUBE', 'VIMEO', 'DIRECT', name='videoplatform'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'EXTRACTING', 'TRANSCRIBING', 'COMPLETED', 'FAILED', name='videostatus'), nullable=False),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)
    op.create_index(op.f('ix_videos_user_id'), 'videos', ['user_id'], unique=False)
    op.create_index(op.f('ix_videos_url_hash'), 'videos', ['url_hash'], unique=True)
    op.create_index(op.f('ix_videos_status'), 'videos', ['status'], unique=False)
    op.create_index(op.f('ix_videos_task_id'), 'videos', ['task_id'], unique=False)

    # Create transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('segments', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('processing_time_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcriptions_id'), 'transcriptions', ['id'], unique=False)
    op.create_index(op.f('ix_transcriptions_video_id'), 'transcriptions', ['video_id'], unique=True)


def downgrade() -> None:
    """Drop transcriptions and videos tables."""
    op.drop_index(op.f('ix_transcriptions_video_id'), table_name='transcriptions')
    op.drop_index(op.f('ix_transcriptions_id'), table_name='transcriptions')
    op.drop_table('transcriptions')
    
    op.drop_index(op.f('ix_videos_task_id'), table_name='videos')
    op.drop_index(op.f('ix_videos_status'), table_name='videos')
    op.drop_index(op.f('ix_videos_url_hash'), table_name='videos')
    op.drop_index(op.f('ix_videos_user_id'), table_name='videos')
    op.drop_index(op.f('ix_videos_id'), table_name='videos')
    op.drop_table('videos')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS videostatus')
    op.execute('DROP TYPE IF EXISTS videoplatform')
