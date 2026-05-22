"""
Summary API endpoints for AI-powered video summarization.
Provides summary generation and retrieval operations.
"""

from celery import chain
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import RequestContext, get_request_context
from src.db.session import get_db
from src.models.summary import Summary
from src.models.video import Video
from src.schemas.summary import (
    SummaryListResponse,
    SummaryRequest,
    SummaryResponse,
)
from src.tasks.extract_highlights import extract_highlights_task
from src.tasks.summarize import generate_summary_task

router = APIRouter(prefix="/videos", tags=["summaries"])


@router.post(
    "/{video_id}/summaries", response_model=SummaryResponse, status_code=status.HTTP_202_ACCEPTED
)
async def generate_summary(
    video_id: int,
    request: SummaryRequest,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """
    Generate AI summary for a transcribed video.

    Triggers async processing pipeline:
    1. Generate summary content
    2. Extract key highlights
    """
    # Verify video exists and belongs to user
    query = db.query(Video).filter(Video.id == video_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    elif context.guest_session:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    video = query.first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Trigger async summary generation pipeline
    task_chain = chain(
        generate_summary_task.s(video_id, request.summary_type.value),
        extract_highlights_task.s(),
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
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SummaryListResponse:
    """Get all summaries for a video."""
    # Verify video ownership
    query = db.query(Video).filter(Video.id == video_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    elif context.guest_session:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
    video = query.first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    summaries = (
        db.query(Summary)
        .filter(Summary.video_id == video_id)
        .order_by(Summary.created_at.desc())
        .all()
    )

    return SummaryListResponse(
        summaries=summaries,
        total=len(summaries),
    )


@router.get("/summaries/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: int,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """Get a specific summary by ID."""
    query = db.query(Summary).join(Video).filter(Summary.id == summary_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    elif context.guest_session:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    summary = query.first()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return summary
