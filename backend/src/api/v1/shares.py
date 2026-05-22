"""
Share API endpoints for timestamp link generation and public access.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user
from src.db.session import get_db
from src.models.user import User
from src.models.video import Video
from src.schemas.share import (
    ShareLinkPublicResponse,
    ShareLinkRequest,
    ShareLinkResponse,
)
from src.services.share_service import share_service

router = APIRouter(tags=["shares"])


@router.post("/videos/{video_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    video_id: int,
    request: ShareLinkRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ShareLinkResponse:
    """Create a shareable timestamp link for a video."""
    # Verify video ownership
    video = (
        db.query(Video)
        .filter(
            Video.id == video_id,
            Video.user_id == current_user.id,
        )
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    link = share_service.create_share_link(
        db=db,
        video_id=video_id,
        user_id=current_user.id,
        start_time=request.start_time,
        end_time=request.end_time,
        title=request.title,
        expires_in_hours=request.expires_in_hours,
    )

    return ShareLinkResponse(
        id=link.id,
        video_id=link.video_id,
        token=link.token,
        share_url=f"/share/{link.token}",
        start_time=link.start_time,
        end_time=link.end_time,
        title=link.title,
        is_active=link.is_active,
        created_at=link.created_at,
        expires_at=link.expires_at,
    )


@router.get("/share/{token}", response_model=ShareLinkPublicResponse)
async def get_shared_content(
    token: str,
    db: Session = Depends(get_db),
) -> ShareLinkPublicResponse:
    """Get publicly shared video content by token (no auth required)."""
    content = share_service.get_public_share_content(db=db, token=token)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared content not found or expired",
        )

    return ShareLinkPublicResponse(**content)
