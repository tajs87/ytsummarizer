"""Guest session model used for anonymous ownership and migration."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.session import Base


class GuestSession(Base):  # type: ignore[misc]
    """Represents an anonymous browser session used for guest mode."""

    __tablename__ = "guest_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    migrated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    videos: Mapped[list[Video]] = relationship("Video", back_populates="guest_session")  # type: ignore[name-defined]

    # Raw token is attached only at runtime for cookie issuance in API responses.
    raw_token: ClassVar[str | None] = None

    def __repr__(self) -> str:
        return f"<GuestSession(id={self.id}, active={self.is_active})>"
