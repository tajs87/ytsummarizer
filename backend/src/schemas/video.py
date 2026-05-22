"""
Pydantic schemas for video endpoints.
"""
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from src.models.video import VideoPlatform, VideoStatus


class VideoSubmitRequest(BaseModel):
    """Request schema for submitting a video URL."""

    url: HttpUrl = Field(
        ...,
        description="YouTube, Vimeo, or direct video URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class VideoResponse(BaseModel):
    """Response schema for video information."""

    id: int = Field(..., description="Video ID")
    url: str = Field(..., description="Original video URL")
    platform: VideoPlatform = Field(..., description="Video platform")
    title: str | None = Field(None, description="Video title")
    duration_seconds: float | None = Field(None, description="Video duration in seconds")
    status: VideoStatus = Field(..., description="Processing status")
    error_message: str | None = Field(None, description="Error message if failed")
    task_id: str | None = Field(None, description="Celery task ID for tracking")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    has_transcription: bool = Field(
        False, description="Whether transcription is available"
    )

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    """Response schema for video list."""

    videos: list[VideoResponse] = Field(..., description="List of user's videos")
    total: int = Field(..., description="Total number of videos")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Items per page")
    is_guest_context: bool = Field(False, description="Whether list is for a guest session")
    history_scope: str = Field("account", description="History scope: account or session")
