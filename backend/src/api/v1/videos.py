"""
Video API endpoints.
Handles video submission, listing, and status checking.
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import RequestContext, get_db, get_request_context
from src.core.errors import VideoNotFoundError
from src.models.video import Video, VideoStatus
from src.schemas.video import VideoListResponse, VideoResponse, VideoSubmitRequest
from src.services.cache_service import cache_service
from src.services.video_extractor import video_extractor
from src.tasks.extract import extract_video_task
from src.tasks.transcribe import transcribe_audio_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post(
    "",
    response_model=VideoResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit video for transcription",
)
async def submit_video(
    request: VideoSubmitRequest,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> VideoResponse:
    """
    Submit a video URL for transcription processing.
    
    Workflow:
    1. Validate URL and detect platform
    2. Check cache for existing transcription
    3. Create Video record with PENDING status
    4. Dispatch Celery task chain: extract -> transcribe
    5. Return video with task_id for progress tracking
    
    Rate limiting is enforced by middleware (10 videos/hour).
    """
    print(f"[DEBUG] Starting video submission: {request.url}", flush=True)
    logger.info(f"[SUBMIT] Starting video submission: {request.url}")
    url_str = str(request.url)
    
    # Generate URL hash for deduplication
    owner_scope = (
        f"user:{context.user.id}" if context.user else f"guest:{context.guest_session.id}"
    )
    url_hash = Video.generate_url_hash(url_str, user_scope=owner_scope)
    print(f"[DEBUG] Generated URL hash: {url_hash}", flush=True)
    logger.info(f"[SUBMIT] Generated URL hash: {url_hash}")
    
    # Check if video already exists for this user
    existing_video = (
        db.query(Video)
        .filter(Video.url_hash == url_hash)
        .filter(Video.user_id == (context.user.id if context.user else None))
        .filter(
            Video.owner_guest_session_id
            == (context.guest_session.id if context.guest_session else None)
        )
        .first()
    )
    print(f"[DEBUG] Existing video check: {existing_video}", flush=True)
    
    if existing_video:
        print(f"[DEBUG] Found existing video: id={existing_video.id}, status={existing_video.status}", flush=True)
        logger.info(f"[SUBMIT] Found existing video: id={existing_video.id}, status={existing_video.status}")
        # Return existing video (may be processing or completed)
        has_transcription = existing_video.transcription is not None
        return VideoResponse(
            id=existing_video.id,
            url=existing_video.url,
            platform=existing_video.platform,
            title=existing_video.title,
            duration_seconds=existing_video.duration_seconds,
            status=existing_video.status,
            error_message=existing_video.error_message,
            task_id=existing_video.task_id,
            created_at=existing_video.created_at,
            completed_at=existing_video.completed_at,
            has_transcription=has_transcription,
        )
    
    logger.info(f"[SUBMIT] No existing video found, extracting metadata...")
    # Detect platform
    metadata = await video_extractor.extract_metadata(url_str)
    platform = metadata["platform"]
    logger.info(f"[SUBMIT] Metadata extracted: platform={platform}")
    
    # Create new video record
    video = Video(
        user_id=context.user.id if context.user else None,
        owner_guest_session_id=context.guest_session.id if context.guest_session else None,
        url=url_str,
        url_hash=url_hash,
        platform=platform,
        status=VideoStatus.PENDING,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Dispatch Celery task chain
    # extract_video_task -> transcribe_audio_task
    task_chain = (
        extract_video_task.s(video.id)
        | transcribe_audio_task.s(video.id)
    )
    result = task_chain.apply_async()
    
    # Update video with task_id
    video.task_id = result.id
    db.commit()
    
    return VideoResponse(
        id=video.id,
        url=video.url,
        platform=video.platform,
        title=video.title,
        duration_seconds=video.duration_seconds,
        status=video.status,
        error_message=video.error_message,
        task_id=video.task_id,
        created_at=video.created_at,
        completed_at=video.completed_at,
        has_transcription=False,
    )


@router.get(
    "",
    response_model=VideoListResponse,
    summary="List user's videos",
)
async def list_videos(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: VideoStatus | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> VideoListResponse:
    """
    List current user's videos with pagination and filtering.
    
    Returns videos ordered by creation date (newest first).
    """
    query = db.query(Video)
    if context.user:
        query = query.filter(Video.user_id == context.user.id)
    else:
        query = query.filter(Video.owner_guest_session_id == context.guest_session.id)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Video.status == status_filter)
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    videos = (
        query.order_by(Video.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    # Convert to response models
    video_responses = []
    for video in videos:
        has_transcription = video.transcription is not None
        video_responses.append(
            VideoResponse(
                id=video.id,
                url=video.url,
                platform=video.platform,
                title=video.title,
                duration_seconds=video.duration_seconds,
                status=video.status,
                error_message=video.error_message,
                task_id=video.task_id,
                created_at=video.created_at,
                completed_at=video.completed_at,
                has_transcription=has_transcription,
            )
        )
    
    return VideoListResponse(
        videos=video_responses,
        total=total,
        page=page,
        page_size=page_size,
        is_guest_context=context.is_guest,
        history_scope="session" if context.is_guest else "account",
    )


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    summary="Get video details",
)
async def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> VideoResponse:
    """
    Get details for a specific video.
    
    Only returns videos owned by the current user.
    """
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
    
    has_transcription = video.transcription is not None
    
    return VideoResponse(
        id=video.id,
        url=video.url,
        platform=video.platform,
        title=video.title,
        duration_seconds=video.duration_seconds,
        status=video.status,
        error_message=video.error_message,
        task_id=video.task_id,
        created_at=video.created_at,
        completed_at=video.completed_at,
        has_transcription=has_transcription,
    )


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete video",
)
async def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    context: RequestContext = Depends(get_request_context),
) -> None:
    """
    Delete a video and its associated transcription.
    
    Only allows deletion of videos owned by the current user.
    """
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
    
    # Invalidate cache
    await cache_service.invalidate_transcription(video.url_hash)
    
    # Delete video (cascade deletes transcription)
    db.delete(video)
    db.commit()
