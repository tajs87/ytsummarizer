"""
Pydantic schemas for shareable link API requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ShareLinkRequest(BaseModel):
    """Request schema for creating shareable link."""

    start_time: float = Field(..., ge=0, description="Start timestamp in seconds")
    end_time: float | None = Field(None, ge=0, description="Optional end timestamp")
    title: str | None = Field(None, max_length=255, description="Optional custom title")
    expires_in_hours: int | None = Field(None, ge=1, le=720, description="Expiration in hours")


class ShareLinkResponse(BaseModel):
    """Response schema for shareable link."""

    id: int
    video_id: int
    token: str
    share_url: str
    start_time: float
    end_time: float | None
    title: str | None
    is_active: bool
    created_at: datetime
    expires_at: datetime | None

    class Config:
        from_attributes = True


class ShareLinkPublicResponse(BaseModel):
    """Public response schema for accessing shared content."""

    video_id: int
    video_title: str | None
    transcription_text: str
    start_time: float
    end_time: float | None
    title: str | None
