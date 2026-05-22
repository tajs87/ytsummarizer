"""Service for atomic migration of guest-owned videos to authenticated users."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.models.guest_session import GuestSession
from src.models.video import Video


class GuestMigrationService:
    """Moves all current guest-session items under a user account atomically."""

    def migrate_guest_items(self, db: Session, guest_session: GuestSession, user_id: int) -> int:
        updated_count = (
            db.query(Video)
            .filter(Video.owner_guest_session_id == guest_session.id)
            .update(
                {
                    Video.user_id: user_id,
                    Video.owner_guest_session_id: None,
                },
                synchronize_session=False,
            )
        )

        guest_session.is_active = False
        guest_session.migrated_at = datetime.now(UTC)
        db.commit()
        return updated_count


# Shared service instance
guest_migration_service = GuestMigrationService()
