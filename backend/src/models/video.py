"""
Video model representing a video resource for transcription.
Tracks video metadata, processing status, and relationships.
"""
import hashlib
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.session import Base


class VideoPlatform(str, PyEnum):
    """Supported video platforms."""
    
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DIRECT = "direct"


class VideoStatus(str, PyEnum):
    """Video processing status state machine."""
    
    PENDING = "pending"  # Initial state after submission
    EXTRACTING = "extracting"  # Downloading video/audio
    TRANSCRIBING = "transcribing"  # Generating transcription
    COMPLETED = "completed"  # Processing successful
    FAILED = "failed"  # Processing failed


class Video(Base):
    """
    Video entity representing a submitted video for transcription.
    
    State transitions:
    PENDING -> EXTRACTING -> TRANSCRIBING -> COMPLETED
           \-> FAILED (at any stage)
    """

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Ownership relationship
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    owner_guest_session_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("guest_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user: Mapped["User | None"] = relationship("User", back_populates="videos")  # type: ignore[name-defined]
    guest_session: Mapped["GuestSession | None"] = relationship("GuestSession", back_populates="videos")  # type: ignore[name-defined]
    
    # Video metadata
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    platform: Mapped[VideoPlatform] = mapped_column(
        Enum(VideoPlatform), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(500))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    
    # Processing status
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus), default=VideoStatus.PENDING, nullable=False, index=True
    )
    error_message: Mapped[str | None] = mapped_column(String(1000))
    
    # Celery task tracking
    task_id: Mapped[str | None] = mapped_column(String(255), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    transcription: Mapped["Transcription"] = relationship(  # type: ignore[name-defined]
        "Transcription", back_populates="video", uselist=False, cascade="all, delete-orphan"
    )
    summaries: Mapped[list["Summary"]] = relationship(  # type: ignore[name-defined]
        "Summary", back_populates="video", cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_url_hash(url: str, user_scope: str | None = None) -> str:
        """
        Generate a unique hash for a video URL.
        Used for deduplication and caching.
        
        Args:
            url: Video URL to hash
            user_scope: Optional user namespace to avoid cross-user collisions
        
        Returns:
            SHA256 hash of the normalized URL
        """
        # Normalize URL: lowercase and strip whitespace
        # Keep query parameters as they're essential for identifying videos
        normalized = url.lower().strip()
        
        # Remove fragment (everything after #)
        if "#" in normalized:
            normalized = normalized.split("#")[0]
        
        if user_scope:
            normalized = f"{user_scope}:{normalized}"

        return hashlib.sha256(normalized.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, url={self.url[:50]}, status={self.status.value})>"


# Add videos relationship to User model
from src.models.guest_session import GuestSession  # noqa: E402
from src.models.user import User  # noqa: E402

User.videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")  # type: ignore
