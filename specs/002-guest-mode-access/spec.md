# Feature Specification: Guest Mode Access

**Feature Branch**: `002-video-transcription-summary`

**Created**: 2026-05-22

**Status**: Draft

**Input**: User description: "add another feature in which the user can also use the features without creating an account, the person only loses history."

## Clarifications

### Session 2026-05-22

- Q: What guest data retention model should be used? → A: Session-only guest data, cleared automatically when the browser session ends.
- Q: How should history behave for guests? → A: Show a guest-only history list for current session items, and clear it on session end.
- Q: What happens to guest items when user signs in mid-session? → A: Automatically migrate all current guest session items into account history after sign-in.
- Q: How should guest session identity be tracked? → A: Use a server-issued anonymous session token stored in a secure httpOnly cookie.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Guest Can Use Core Features (Priority: P1)

As a first-time visitor, I can submit a video and receive transcription/summary results without creating an account.

**Why this priority**: This removes the highest-friction step and enables immediate product value.

**Independent Test**: Can be fully tested by opening the app in a fresh browser session, skipping sign-in, submitting a valid video URL, and verifying transcript and summary are displayed.

**Acceptance Scenarios**:

1. **Given** a user is not signed in, **When** they submit a valid supported video URL, **Then** the system processes the video and shows transcription results.
2. **Given** a user is not signed in, **When** processing completes, **Then** the user can view generated summaries and highlights for that video.
3. **Given** a user is not signed in, **When** they reopen the app in a new session, **Then** prior guest history is not available.

---

### User Story 2 - Signed-In Users Keep History (Priority: P2)

As a signed-in user, I can continue using the product with persistent history so guest mode does not reduce existing account benefits.

**Why this priority**: Preserves existing value for registered users while introducing guest access.

**Independent Test**: Can be tested by signing in, submitting a video, and confirming it appears in history after browser refresh and session restart.

**Acceptance Scenarios**:

1. **Given** a user is signed in, **When** they submit and process a video, **Then** the item appears in their history list.
2. **Given** a user is signed in, **When** they return later, **Then** previously processed videos remain visible in history.

---

### User Story 3 - Clear Guest History Expectations (Priority: P3)

As a guest user, I can clearly understand that my results are temporary and tied only to the current session.

**Why this priority**: Reduces confusion and support issues about missing history.

**Independent Test**: Can be tested by using guest mode and verifying history messaging explains temporary access before and after processing.

**Acceptance Scenarios**:

1. **Given** a user is in guest mode, **When** they visit history-related views, **Then** the UI explains that guest history is not retained after session loss.
2. **Given** a guest user chooses to sign in or register, **When** they complete authentication, **Then** all current-session guest items are automatically migrated into account history.
3. **Given** a user is in guest mode, **When** they open history, **Then** they see a guest-only list of items from the active session.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Guest user opens multiple tabs in the same browser session: all tabs should access the same guest session context consistently.
- Guest session expires or is cleared while processing is still running: completed output should still be viewable from the active result page, but not added to persistent history.
- User submits duplicate URLs in guest mode: duplicates should be handled consistently with existing deduplication behavior for the active context.
- Guest user signs in mid-session while items are pending/transcribing: all current-session items (including in-progress) must be migrated to account history with consistent ownership.
- Guest user refreshes or reopens after the browser session ends: previously generated guest history and guest summary listings are no longer available.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow users to submit supported video URLs and run transcription without requiring account creation.
- **FR-002**: System MUST allow guest users to view transcription output and generated summaries for videos submitted during their active session.
- **FR-003**: System MUST keep persistent video history only for authenticated users.
- **FR-004**: System MUST ensure guest-accessed items are not listed in persistent account history before authentication.
- **FR-005**: System MUST clearly indicate in the interface when a user is in guest mode and that guest history is temporary.
- **FR-006**: System MUST preserve existing authenticated history behavior and not remove or alter previously saved account history.
- **FR-007**: System MUST provide a path for guest users to authenticate at any time without blocking current processing flows.
- **FR-008**: System MUST handle authorization for history endpoints so guest users receive guest-appropriate responses rather than generic failure messages.
- **FR-009**: System MUST scope guest history and guest-generated results visibility to the active browser session only and clear guest history when that session ends.
- **FR-010**: System MUST provide a guest-only history view that lists only current-session guest items and is unavailable after session end.
- **FR-011**: System MUST automatically migrate all current-session guest items into authenticated account history immediately after successful sign-in or registration.
- **FR-012**: System MUST track guest session identity using a server-issued anonymous session token stored in a secure httpOnly cookie.

### Key Entities *(include if feature involves data)*

- **Guest Session Context**: Represents temporary user context for non-authenticated usage, identified by a server-issued anonymous session token in a secure httpOnly cookie; includes active processing items and current-session visibility rules.
- **History Entry**: Represents a processed video item and its result metadata; belongs to either persistent authenticated history or temporary guest-only visibility.
- **Account User**: Represents an authenticated identity with durable ownership of history entries across sessions.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 90% of first-time users can submit a video and reach a visible transcription result without creating an account.
- **SC-002**: 100% of authenticated users retain access to their prior history entries after guest-mode feature rollout.
- **SC-003**: At least 95% of guest sessions display clear messaging that history is temporary before the user leaves the session.
- **SC-004**: Guest-mode related support complaints about "missing history" decrease by at least 50% after release.

## Assumptions

- Existing sign-in and registration flows remain available and unchanged in capability.
- Guest mode data retention is session-only and automatically cleared when the browser session ends.
- History persistence continues to be tied to authenticated identity only.
- Guest items become authenticated history only after user authentication succeeds in the same session.
- Anonymous session token issuance and secure cookie behavior are available in the deployment environment.
- Current transcription and summarization processing behavior remains the same regardless of guest or authenticated mode.
