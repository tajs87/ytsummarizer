"""
Structured error handling and custom exception classes.
Per constitution requirement: errors must be actionable with error codes.
"""

from typing import Any


class YTSumError(Exception):
    """
    Base exception for all YTSum application errors.
    All custom exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Video-related errors (VID-xxx)
class VideoNotFoundError(YTSumError):
    """Video not found in database."""

    def __init__(self, video_id: str | int):
        super().__init__(
            message=f"Video with ID {video_id} not found",
            error_code="VID-001",
            status_code=404,
            details={"video_id": str(video_id)},
        )


class VideoExtractionError(YTSumError):
    """Failed to extract video from URL."""

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(
            message=message or "Failed to extract video from URL",
            error_code="VID-002",
            status_code=400,
            details=details or {},
        )


class VideoDurationExceededError(YTSumError):
    """Video duration exceeds maximum allowed."""

    def __init__(self, duration_hours: float, max_hours: int):
        super().__init__(
            message=f"Video duration ({duration_hours:.1f}h) exceeds maximum allowed ({max_hours}h)",
            error_code="VID-003",
            status_code=400,
            details={"duration_hours": duration_hours, "max_hours": max_hours},
        )


# Transcription errors (TRN-xxx)
class TranscriptionNotFoundError(YTSumError):
    """Transcription not found."""

    def __init__(self, transcription_id: int | str):
        super().__init__(
            message=f"Transcription with ID {transcription_id} not found",
            error_code="TRN-001",
            status_code=404,
            details={"transcription_id": str(transcription_id)},
        )


class TranscriptionFailedError(YTSumError):
    """Transcription processing failed."""

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(
            message=message or "Transcription processing failed",
            error_code="TRN-002",
            status_code=500,
            details=details or {},
        )


# Summary errors (SUM-xxx)
class SummaryNotFoundError(YTSumError):
    """Summary not found."""

    def __init__(self, summary_id: int | str):
        super().__init__(
            message=f"Summary with ID {summary_id} not found",
            error_code="SUM-001",
            status_code=404,
            details={"summary_id": str(summary_id)},
        )


class SummarizationFailedError(YTSumError):
    """Summarization processing failed."""

    def __init__(self, transcription_id: int | str, reason: str):
        super().__init__(
            message="Summarization processing failed",
            error_code="SUM-002",
            status_code=500,
            details={"transcription_id": str(transcription_id), "reason": reason},
        )


# Rate limiting errors (RATE-xxx)
class RateLimitExceededError(YTSumError):
    """User has exceeded rate limit."""

    def __init__(self, limit: int, reset_at: str):
        super().__init__(
            message=f"Rate limit exceeded. Maximum {limit} videos per hour.",
            error_code="RATE-001",
            status_code=429,
            details={"limit": limit, "reset_at": reset_at},
        )


# Authentication errors (AUTH-xxx)
class InvalidCredentialsError(YTSumError):
    """Invalid authentication credentials."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password",
            error_code="AUTH-001",
            status_code=401,
        )


class TokenExpiredError(YTSumError):
    """JWT token has expired."""

    def __init__(self) -> None:
        super().__init__(
            message="Authentication token has expired",
            error_code="AUTH-002",
            status_code=401,
        )


class InsufficientPermissionsError(YTSumError):
    """User lacks required permissions."""

    def __init__(self, required_permission: str):
        super().__init__(
            message="Insufficient permissions for this operation",
            error_code="AUTH-003",
            status_code=403,
            details={"required_permission": required_permission},
        )
