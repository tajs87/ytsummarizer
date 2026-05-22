"""
Highlight model for storing key moments extracted from video transcriptions.
Each highlight represents an important quote or segment with timestamp references.
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from src.db.session import Base


class Highlight(Base):
    """Key moment or important quote from video transcription."""

    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # Timestamp in seconds
    end_time = Column(Float, nullable=False)  # Timestamp in seconds
    importance_score = Column(Float, nullable=True)  # 0.0-1.0 relevance score
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    summary = relationship("Summary", back_populates="highlights")

    def __repr__(self) -> str:
        return f"<Highlight(id={self.id}, summary_id={self.summary_id}, start={self.start_time}s)>"

    @property
    def duration(self) -> float:
        """Calculate duration of the highlight in seconds."""
        return self.end_time - self.start_time
