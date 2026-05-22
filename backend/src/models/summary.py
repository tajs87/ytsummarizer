"""
Summary model for storing AI-generated video summaries.
Supports multiple summary types (brief, detailed, bullet points).
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.db.session import Base


class SummaryType(enum.StrEnum):
    """Types of summaries that can be generated."""

    BRIEF = "brief"  # Short 2-3 sentence overview
    DETAILED = "detailed"  # Comprehensive multi-paragraph summary
    BULLET_POINTS = "bullet_points"  # Key points in list format


class Summary(Base):
    """AI-generated summary of video transcription."""

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    summary_type = Column(SQLEnum(SummaryType), nullable=False, default=SummaryType.BRIEF)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    video = relationship("Video", back_populates="summaries")
    highlights = relationship("Highlight", back_populates="summary", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Summary(id={self.id}, video_id={self.video_id}, type={self.summary_type})>"
