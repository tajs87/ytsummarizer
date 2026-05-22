"""
Pydantic schemas for transcription endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    """Schema for a single transcription segment."""

    id: int = Field(..., description="Segment ID")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text for this segment")
    speaker: str | None = Field(None, description="Speaker identifier if detected")


class TranscriptionResponse(BaseModel):
    """Response schema for transcription data."""

    id: int = Field(..., description="Transcription ID")
    video_id: int = Field(..., description="Associated video ID")
    full_text: str = Field(..., description="Complete transcription text")
    segments: list[TranscriptionSegment] = Field(..., description="Timed transcription segments")
    language: str = Field(..., description="Detected language code")
    word_count: int = Field(..., description="Total word count")
    processing_time_seconds: float | None = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class TranscriptionSearchRequest(BaseModel):
    """Request schema for searching within transcription."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Search term to find in transcription",
        examples=["important", "conclusion", "summary"],
    )


class TranscriptionSearchResult(BaseModel):
    """Single search result with context."""

    segment: TranscriptionSegment = Field(..., description="Matching segment")
    match_count: int = Field(..., description="Number of matches in this segment")


class TranscriptionSearchResponse(BaseModel):
    """Response schema for transcription search."""

    query: str = Field(..., description="Original search query")
    total_matches: int = Field(..., description="Total number of matching segments")
    results: list[TranscriptionSearchResult] = Field(
        ..., description="Matching segments with context"
    )
