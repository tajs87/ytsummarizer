"""
Service for managing shareable timestamp links.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src.models.shareable_link import ShareableLink
from src.models.video import Video
from src.models.transcription import Transcription
from src.utils.token_generator import generate_share_token


class ShareService:
    """Service for creating and retrieving shareable links."""

    def create_share_link(
        self,
        db: Session,
        video_id: int,
        user_id: int,
        start_time: float,
        end_time: float | None = None,
        title: str | None = None,
        expires_in_hours: int | None = None,
    ) -> ShareableLink:
        """Create a new shareable link."""
        # Generate unique token
        token = generate_share_token()
        while db.query(ShareableLink).filter(ShareableLink.token == token).first():
            token = generate_share_token()

        # Calculate expiration
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        link = ShareableLink(
            video_id=video_id,
            user_id=user_id,
            token=token,
            start_time=start_time,
            end_time=end_time,
            title=title,
            expires_at=expires_at,
        )

        db.add(link)
        db.commit()
        db.refresh(link)

        return link

    def get_public_share_content(
        self,
        db: Session,
        token: str,
    ) -> dict | None:
        """Get publicly accessible shared content by token."""
        link = db.query(ShareableLink).filter(
            ShareableLink.token == token,
            ShareableLink.is_active == True,
        ).first()

        if not link:
            return None

        # Check expiration
        if link.expires_at and link.expires_at < datetime.now(timezone.utc):
            return None

        # Get related video and transcription
        video = db.query(Video).filter(Video.id == link.video_id).first()
        transcription = db.query(Transcription).filter(
            Transcription.video_id == link.video_id
        ).first()

        if not video or not transcription:
            return None

        return {
            "video_id": video.id,
            "video_title": video.title,
            "transcription_text": transcription.full_text,
            "start_time": link.start_time,
            "end_time": link.end_time,
            "title": link.title,
        }


share_service = ShareService()
