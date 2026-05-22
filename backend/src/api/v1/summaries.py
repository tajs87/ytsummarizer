"""
Summary API endpoints for AI-powered video summarization.
Provides summary generation and retrieval operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from celery import chain

from src.api.deps import get_current_active_user
from src.db.session import get_db
from src.models.user import User
from src.models.video import Video
from src.models.summary import Summary
from src.schemas.summary import (
    SummaryRequest,
    SummaryResponse,
    SummaryListResponse,
)
from src.tasks.summarize import generate_summary_task
from src.tasks.extract_highlights import extract_highlights_task

router = APIRouter(prefix="/videos", tags=["summaries"])


@router.post("/{video_id}/summaries", response_model=SummaryResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_summary(
    video_id: int,
    request: SummaryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """
    Generate AI summary for a transcribed video.

    Triggers async processing pipeline:
    1. Generate summary content
    2. Extract key highlights
    """
    # Verify video exists and belongs to user
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id,
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Trigger async summary generation pipeline
    task_chain = chain(
        generate_summary_task.s(video_id, request.summary_type.value),
    )
    task_chain.apply_async()

    # Return placeholder response for async operation
    return SummaryResponse(
        id=0,
        video_id=video_id,
        summary_type=request.summary_type,
        content="Summary generation in progress...",
        highlights=[],
        created_at=video.created_at,
        updated_at=video.updated_at,
    )


@router.get("/{video_id}/summaries", response_model=SummaryListResponse)
async def get_video_summaries(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SummaryListResponse:
    """Get all summaries for a video."""
    # Verify video ownership
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id,
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    summaries = db.query(Summary).filter(Summary.video_id == video_id).all()

    return SummaryListResponse(
        summaries=summaries,
        total=len(summaries),
    )


@router.get("/summaries/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """Get a specific summary by ID."""
    summary = db.query(Summary).join(Video).filter(
        Summary.id == summary_id,
        Video.user_id == current_user.id,
    ).first()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return summary
