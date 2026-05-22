"""
Pydantic schemas for summary API requests and responses.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from src.schemas.highlight import HighlightResponse


class SummaryType(StrEnum):
    """Supported summary generation types."""

    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"


class SummaryRequest(BaseModel):
    """Request schema for generating video summary."""

    summary_type: SummaryType = Field(default=SummaryType.BRIEF, description="Type of summary to generate")


class SummaryBase(BaseModel):
    """Base summary schema with common fields."""

    summary_type: SummaryType
    content: str = Field(..., min_length=1, description="Generated summary content")


class SummaryResponse(SummaryBase):
    """Schema for summary response."""

    id: int
    video_id: int
    highlights: list[HighlightResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SummaryListResponse(BaseModel):
    """Schema for list of summaries."""

    summaries: list[SummaryResponse]
    total: int = Field(..., ge=0)
