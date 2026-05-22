"""
Pydantic schemas for error responses.
Provides structured, consistent error format across all endpoints.
"""
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Additional context about the error."""

    model_config = {"extra": "allow"}  # Allow arbitrary fields in details


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Per constitution requirement: Errors must be actionable with clear codes.

    Example:
        {
            "error_code": "VID-001",
            "message": "Video not found",
            "details": {"video_id": "123"}
        }
    """

    error_code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling",
        examples=["VID-001", "TRN-002", "AUTH-001"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message with guidance",
        examples=["Video with ID 123 not found"],
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context and debugging information",
        examples=[{"video_id": "123", "reason": "Invalid URL"}],
    )


class ValidationErrorDetail(BaseModel):
    """Details for a single validation error field."""

    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    type: str = Field(..., description="Type of validation error")


class ValidationErrorResponse(BaseModel):
    """
    Response for request validation errors (422).

    FastAPI returns this automatically for Pydantic validation errors.
    """

    error_code: str = Field(default="VAL-001", description="Validation error code")
    message: str = Field(
        default="Request validation failed",
        description="General validation error message",
    )
    details: list[ValidationErrorDetail] = Field(
        ..., description="List of field-specific validation errors"
    )
