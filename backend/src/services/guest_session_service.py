"""Guest session token and persistence service."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.models.guest_session import GuestSession


@dataclass
class GuestSessionResult:
    """Result container for guest-session bootstrap and refresh operations."""

    session: GuestSession
    token: str
    is_new: bool


class GuestSessionService:
    """Creates, validates, and refreshes server-issued anonymous guest sessions."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def create_guest_session(self, db: Session, token: str | None = None) -> GuestSession:
        raw_token = token or self.generate_token()
        token_hash = self._hash_token(raw_token)

        now = datetime.now(UTC)
        guest_session = GuestSession(
            token_hash=token_hash,
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(seconds=self.settings.guest_session_max_age_seconds),
            is_active=True,
        )
        guest_session.raw_token = raw_token
        db.add(guest_session)
        db.commit()
        db.refresh(guest_session)
        return guest_session

    def get_active_session(self, db: Session, token: str) -> GuestSession | None:
        token_hash = self._hash_token(token)
        now = datetime.now(UTC)

        session = (
            db.query(GuestSession)
            .filter(GuestSession.token_hash == token_hash, GuestSession.is_active.is_(True))
            .first()
        )
        if not session:
            return None

        if session.expires_at <= now:
            session.is_active = False
            db.commit()
            return None

        return session

    def touch_session(self, db: Session, session: GuestSession) -> GuestSession:
        now = datetime.now(UTC)
        session.last_seen_at = now
        session.expires_at = now + timedelta(seconds=self.settings.guest_session_max_age_seconds)
        db.commit()
        db.refresh(session)
        return session

    def bootstrap(self, db: Session, token: str | None) -> GuestSessionResult:
        """Create or refresh guest session from optional cookie token."""
        if token:
            existing = self.get_active_session(db, token)
            if existing:
                self.touch_session(db, existing)
                return GuestSessionResult(session=existing, token=token, is_new=False)

        session = self.create_guest_session(db)
        return GuestSessionResult(session=session, token=session.raw_token or self.generate_token(), is_new=True)


# Shared service instance
guest_session_service = GuestSessionService()
