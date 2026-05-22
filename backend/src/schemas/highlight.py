"""
Pydantic schemas for highlight API requests and responses.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class HighlightBase(BaseModel):
    """Base highlight schema with common fields."""

    text: str = Field(..., min_length=1, description="Highlight text content")
    start_time: float = Field(..., ge=0, description="Start timestamp in seconds")
    end_time: float = Field(..., ge=0, description="End timestamp in seconds")
    importance_score: float | None = Field(None, ge=0, le=1, description="Importance score 0-1")


class HighlightResponse(HighlightBase):
    """Schema for highlight response."""

    id: int
    summary_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HighlightListResponse(BaseModel):
    """Schema for list of highlights."""

    highlights: list[HighlightResponse]
    total: int = Field(..., ge=0)
