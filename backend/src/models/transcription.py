"""
Transcription model for storing video transcription data.
Uses JSONB for flexible segment storage with timestamps.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.session import Base


class Transcription(Base):
    """
    Transcription entity containing full text and timing segments.
    
    Segments format (JSONB):
    [
        {
            "id": 0,
            "start": 0.0,
            "end": 5.2,
            "text": "Welcome to this video...",
            "speaker": "Speaker 1" (optional)
        },
        ...
    ]
    """

    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Video relationship (one-to-one)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id"), unique=True, nullable=False, index=True
    )
    video: Mapped["Video"] = relationship("Video", back_populates="transcription")  # type: ignore[name-defined]
    
    # Transcription content
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    
    # Metadata
    language: Mapped[str] = mapped_column(
        String(10), default="en", nullable=False
    )
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Processing metrics
    processing_time_seconds: Mapped[float | None] = mapped_column(Integer)
    
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

    def search_text(self, query: str) -> list[dict[str, Any]]:
        """
        Search for query in transcription segments.
        
        Args:
            query: Search term (case-insensitive)
        
        Returns:
            List of matching segments with context
        
        Example:
            >>> results = transcription.search_text("important")
            >>> # Returns segments containing "important"
        """
        query_lower = query.lower()
        results = []
        
        for segment in self.segments:
            if query_lower in segment.get("text", "").lower():
                results.append(segment)
        
        return results

    def __repr__(self) -> str:
        return f"<Transcription(id={self.id}, video_id={self.video_id}, words={self.word_count})>"
