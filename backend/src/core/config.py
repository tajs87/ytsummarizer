"""
Application configuration using pydantic-settings.
Loads from environment variables with validation.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with type validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: PostgresDsn
    
    # Redis
    redis_url: RedisDsn
    
    # OpenAI API
    openai_api_key: str = Field(..., min_length=1)
    
    # Security
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    guest_session_cookie_name: str = "ytsum_guest_session"
    guest_session_max_age_seconds: int = 86400
    guest_session_secure_cookie: bool = False
    guest_session_same_site: Literal["lax", "strict", "none"] = "lax"
    
    # Application
    debug: bool = False
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )
    max_video_duration_hours: int = 3
    rate_limit_videos_per_hour: int = 10
    
    # Celery
    celery_broker_url: RedisDsn | None = None
    celery_result_backend: RedisDsn | None = None
    
    # Storage
    temp_storage_path: str = "/tmp/ytsum"
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def set_celery_broker(cls, v: str | None, info: dict) -> str:  # type: ignore
        """Default celery_broker_url to redis_url if not set."""
        if v is None and "redis_url" in info.data:
            return str(info.data["redis_url"])
        return v  # type: ignore

    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def set_celery_result(cls, v: str | None, info: dict) -> str:  # type: ignore
        """Default celery_result_backend to redis_url/1 if not set."""
        if v is None and "redis_url" in info.data:
            redis_url = str(info.data["redis_url"])
            # Change database number to 1 for results
            return redis_url.rsplit("/", 1)[0] + "/1"
        return v  # type: ignore


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
