# Quickstart: Guest Mode Access

## Goal

Validate that users can use transcription/summarization without account creation, see guest-only session history, and have guest items auto-migrate to account history upon authentication.

## Prerequisites

- Application stack running (backend, worker, frontend, postgres, redis)
- Browser with clean profile or private session

## Scenario 1: Guest submits and views results

1. Open app without signing in.
2. Submit a supported video URL.
3. Confirm processing progresses and transcript is viewable.
4. Generate summary and verify summary content appears.

Expected:
- Feature works without account.
- No auth wall blocks submit/transcript/summary.

## Scenario 2: Guest-only current-session history

1. While still not signed in, open history view.
2. Confirm list contains guest-session items created in this session.
3. Open a second tab in same browser session and confirm same guest-session items are visible.

Expected:
- Guest history is visible for current session only.
- History is scoped to active guest session context.

## Scenario 3: Session end clears guest history

1. Close browser session fully (or clear session context).
2. Re-open app still not signed in.
3. Open history view.

Expected:
- Prior guest-session history is no longer available.
- UI indicates temporary nature of guest history.

## Scenario 4: Auto-migration on sign-in/register

1. In active guest session with at least one processed item, sign in or register.
2. Navigate to authenticated history.

Expected:
- All current-session guest items are now present in authenticated history.
- Guest history context is no longer used for those migrated items.

## API verification checklist

- POST /api/v1/guest/session issues/refreshes guest session cookie
- POST /api/v1/videos works with guest session cookie
- GET /api/v1/videos returns guest-session list when unauthenticated
- POST /api/v1/auth/login triggers migration when guest cookie present

## Regression checklist

- Existing authenticated-only behavior remains intact for users with prior history.
- Rate limiting and validation still apply to guest submissions.
- Summary and highlight generation remains functional for guest-created items pre- and post-migration.
