"""
Transcription API endpoints.
Handles transcription retrieval, search, and export.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from src.api.deps import RequestContext, get_db, get_request_context
from src.models.transcription import Transcription
from src.models.video import Video
from src.schemas.transcription import (
    TranscriptionResponse,
    TranscriptionSearchRequest,
    TranscriptionSearchResponse,
    TranscriptionSearchResult,
    TranscriptionSegment,
)

router = APIRouter(prefix="/videos", tags=["transcriptions"])


@router.get(
    "/{video_id}/transcription",
    response_model=TranscriptionResponse,
    summary="Get video transcription",
)
async def get_transcription(
    video_id: int,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> TranscriptionResponse:
    """
    Retrieve transcription for a video.

    Returns full transcription with segments and timestamps.
    Only accessible by video owner.
    """
    # Verify video ownership
    query = db.query(Video).filter(Video.id == video_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    else:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    video = query.first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    # Get transcription
    transcription = db.query(Transcription).filter(Transcription.video_id == video_id).first()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription not available for video {video_id}",
        )

    # Convert segments to response format
    segments = [TranscriptionSegment(**segment) for segment in transcription.segments]

    return TranscriptionResponse(
        id=transcription.id,
        video_id=transcription.video_id,
        full_text=transcription.full_text,
        segments=segments,
        language=transcription.language,
        word_count=transcription.word_count,
        processing_time_seconds=transcription.processing_time_seconds,
        created_at=transcription.created_at,
    )


@router.post(
    "/{video_id}/transcription/search",
    response_model=TranscriptionSearchResponse,
    summary="Search within transcription",
)
async def search_transcription(
    video_id: int,
    request: TranscriptionSearchRequest,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> TranscriptionSearchResponse:
    """
    Search for text within a video's transcription.

    Returns matching segments with context and timestamps.
    Case-insensitive search.
    """
    # Verify video ownership
    query = db.query(Video).filter(Video.id == video_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    else:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    video = query.first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    # Get transcription
    transcription = db.query(Transcription).filter(Transcription.video_id == video_id).first()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription not available for video {video_id}",
        )

    # Perform search
    matching_segments = transcription.search_text(request.query)

    # Format results
    results = []
    for segment in matching_segments:
        # Count occurrences of query in segment text
        match_count = segment["text"].lower().count(request.query.lower())

        results.append(
            TranscriptionSearchResult(
                segment=TranscriptionSegment(**segment),
                match_count=match_count,
            )
        )

    return TranscriptionSearchResponse(
        query=request.query,
        total_matches=len(results),
        results=results,
    )


@router.get(
    "/{video_id}/transcription/export",
    response_class=PlainTextResponse,
    summary="Export transcription as plain text",
)
async def export_transcription(
    video_id: int,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> str:
    """
    Export transcription as plain text file.

    Returns transcription with timestamps for each segment.
    Format:
    [00:00:00] First segment text
    [00:00:05] Second segment text
    ...
    """
    # Verify video ownership
    query = db.query(Video).filter(Video.id == video_id)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    else:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    video = query.first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {video_id} not found",
        )

    # Get transcription
    transcription = db.query(Transcription).filter(Transcription.video_id == video_id).first()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription not available for video {video_id}",
        )

    # Format as timestamped text
    lines = []
    lines.append(f"# Transcription: {video.title or 'Untitled'}")
    lines.append(f"# Video URL: {video.url}")
    lines.append(f"# Language: {transcription.language}")
    lines.append(f"# Words: {transcription.word_count}")
    lines.append("")

    for segment in transcription.segments:
        # Format timestamp as HH:MM:SS
        start_seconds = int(segment["start"])
        hours = start_seconds // 3600
        minutes = (start_seconds % 3600) // 60
        seconds = start_seconds % 60
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        lines.append(f"[{timestamp}] {segment['text']}")

    return "\n".join(lines)
