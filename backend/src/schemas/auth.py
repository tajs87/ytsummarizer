"""
Pydantic schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)",
    )


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    migrated_items: int = Field(0, description="Number of guest items migrated on login")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    is_active: bool = Field(..., description="Whether user account is active")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")

    model_config = {"from_attributes": True}
