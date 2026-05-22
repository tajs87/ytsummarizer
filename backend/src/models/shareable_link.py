"""
Shareable link model for timestamp-based video sharing.
Stores secure tokens for public access to specific video moments.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.db.session import Base


class ShareableLink(Base):
    """Model for shareable timestamp links."""

    __tablename__ = "shareable_links"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    token = Column(String(255), unique=True, nullable=False, index=True)
    start_time = Column(Float, nullable=False)  # Timestamp in seconds
    end_time = Column(Float, nullable=True)  # Optional end timestamp
    title = Column(String(255), nullable=True)  # Optional custom title
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration

    # Relationships
    video = relationship("Video")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<ShareableLink(id={self.id}, token={self.token[:8]}...)>"
