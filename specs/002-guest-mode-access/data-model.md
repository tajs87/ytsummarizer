# Data Model: Guest Mode Access

## Entity Overview

- GuestSessionContext
- HistoryEntry (existing video-centric record, ownership-context aware)
- AccountUser (existing authenticated user)

## GuestSessionContext

Represents temporary identity and session metadata for non-authenticated usage.

Attributes:
- id (uuid): Internal guest session identifier
- token_hash (string, unique): Hashed server-issued anonymous token
- created_at (timestamp)
- expires_at (timestamp/session-bound)
- last_seen_at (timestamp)
- is_active (boolean)

Validation:
- token_hash unique and non-reversible representation
- expires_at > created_at
- inactive sessions cannot create new guest entries

Relationships:
- One GuestSessionContext to many HistoryEntry records while unauthenticated

State transitions:
- active -> expired
- active -> migrated (when authentication succeeds)

## HistoryEntry (extension of existing video/transcription aggregate)

Represents a processed item and associated metadata, now with ownership context.

Ownership attributes:
- owner_user_id (nullable FK -> users.id)
- owner_guest_session_id (nullable FK -> guest_sessions.id)

Constraints:
- Exactly one ownership context must be active before migration.
- During migration, ownership transitions atomically from guest_session to user.

Behavior rules:
- Guest list queries return only entries owned by active guest session.
- Authenticated history queries return only entries owned by authenticated user.
- After migration, migrated entries are visible in authenticated history and not guest history.

## AccountUser (existing)

No structural change required beyond receiving migrated ownership for guest-created entries.

## Migration transaction model

Trigger: successful sign-in/registration in a request carrying valid active guest token.

Atomic steps:
1. Resolve active guest session context.
2. Reassign all guest-owned entries to authenticated user.
3. Mark guest session migrated/inactive.
4. Commit transaction.

Failure handling:
- Any failure rolls back entire migration.
- Authentication success should not leave partial ownership reassignment.

## Derived and indexed access patterns

Recommended indexes:
- history(owner_user_id, created_at desc)
- history(owner_guest_session_id, created_at desc)
- guest_sessions(token_hash)

Query patterns:
- Guest history listing by owner_guest_session_id
- Authenticated history listing by owner_user_id
- Migration bulk update by owner_guest_session_id
