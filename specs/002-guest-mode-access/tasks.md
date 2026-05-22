# Tasks: Guest Mode Access

**Input**: Design documents from /specs/002-guest-mode-access/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Introduce project configuration, tooling, and baseline test scaffolding for guest mode.

- [ ] T001 Add guest-session cookie configuration settings in backend/src/core/config.py
- [ ] T002 Add guest-session environment defaults in backend/.env.example
- [ ] T003 [P] Add guest-mode frontend environment notes in frontend/.env.example
- [ ] T004 [P] Add backend test fixtures for guest session cookie context in backend/tests/conftest.py
- [ ] T005 [P] Add frontend test utilities for credentialed API client and auth context in frontend/tests/utils/testProviders.tsx

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core ownership/session infrastructure required by all user stories.

**CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T006 Create migration for guest session table and guest ownership columns in backend/src/db/migrations/versions/005_add_guest_session_ownership.py
- [ ] T007 Implement GuestSession ORM model in backend/src/models/guest_session.py
- [ ] T008 Update Video ownership fields/relationships for guest sessions in backend/src/models/video.py
- [ ] T009 [P] Implement guest session token issuance/verification service in backend/src/services/guest_session_service.py
- [ ] T010 Implement request context dependency for authenticated-or-guest access in backend/src/api/deps.py
- [ ] T011 Enable credentialed cookie CORS policy for frontend origin in backend/src/api/middleware.py
- [ ] T012 Update API client to send credentials for cookie-based guest context in frontend/src/services/api.ts
- [ ] T013 [P] Add ownership and guest session indexes for list and migration queries in backend/src/db/migrations/versions/006_add_guest_ownership_indexes.py

**Checkpoint**: Guest session identity and ownership model is operational.

---

## Phase 3: User Story 1 - Guest Can Use Core Features (Priority: P1)

**Goal**: Unauthenticated users can submit videos and view transcript and summary data in the active session.

**Independent Test**: In a fresh browser session without sign-in, submit a supported URL and view transcript and summary successfully.

### Tests for User Story 1

- [ ] T014 [P] [US1] Add contract test for POST /api/v1/guest/session in backend/tests/contract/test_guest_session_contract.py
- [ ] T015 [P] [US1] Add contract tests for guest-capable /api/v1/videos endpoints in backend/tests/contract/test_guest_videos_contract.py
- [ ] T016 [P] [US1] Add integration test for guest submit to transcript flow in backend/tests/integration/test_guest_submit_transcript.py
- [ ] T017 [P] [US1] Add integration test for guest summary create and retrieval flow in backend/tests/integration/test_guest_summary_flow.py
- [ ] T018 [P] [US1] Add frontend component test for guest summary panel states in frontend/tests/components/SummaryPanel.guest.test.tsx

### Implementation for User Story 1

- [ ] T019 [US1] Add guest session bootstrap endpoint in backend/src/api/v1/guest.py
- [ ] T020 [US1] Register guest API router in backend/src/main.py
- [ ] T021 [US1] Allow guest context in video submission endpoint in backend/src/api/v1/videos.py
- [ ] T022 [US1] Allow guest context in video detail/list ownership checks in backend/src/api/v1/videos.py
- [ ] T023 [US1] Allow guest context for transcript retrieval in backend/src/api/v1/transcriptions.py
- [ ] T024 [US1] Allow guest context for summary create/list/get endpoints in backend/src/api/v1/summaries.py
- [ ] T025 [P] [US1] Add frontend guest-session initializer hook in frontend/src/hooks/useGuestSession.ts
- [ ] T026 [US1] Integrate guest-session bootstrap on app load in frontend/src/App.tsx
- [ ] T027 [US1] Enable guest submit flow without authentication gate in frontend/src/pages/Home.tsx
- [ ] T028 [US1] Ensure summary panel works for guest-owned videos in frontend/src/components/SummaryPanel.tsx

**Checkpoint**: Guest users can process and view a video in-session without account creation.

---

## Phase 4: User Story 2 - Signed-In Users Keep History (Priority: P2)

**Goal**: Authenticated history behavior remains intact and all current guest-session items migrate at login or register.

**Independent Test**: Start as guest with processed and in-progress items, sign in or register, then verify all session items appear in authenticated history.

### Tests for User Story 2

- [ ] T029 [P] [US2] Add integration test for atomic guest-to-user migration at login in backend/tests/integration/test_guest_migration_login.py
- [ ] T030 [P] [US2] Add integration test for register-plus-auth migration path in backend/tests/integration/test_guest_migration_register.py
- [ ] T031 [P] [US2] Add integration test for migrating in-progress guest items in backend/tests/integration/test_guest_migration_in_progress.py
- [ ] T032 [P] [US2] Add frontend integration test for history refetch after auth transition in frontend/tests/integration/authMigrationHistory.test.tsx

### Implementation for User Story 2

- [ ] T033 [US2] Implement atomic migration service from guest ownership to user ownership in backend/src/services/guest_migration_service.py
- [ ] T034 [US2] Invoke guest-item migration on successful login in backend/src/api/v1/auth.py
- [ ] T035 [US2] Invoke guest-item migration on successful register-auth path in backend/src/api/v1/auth.py
- [ ] T036 [US2] Preserve authenticated history query behavior with migrated ownership in backend/src/api/v1/videos.py
- [ ] T037 [P] [US2] Invalidate and refetch history after authentication transition in frontend/src/hooks/useAuth.tsx
- [ ] T038 [US2] Show migration success feedback after sign-in and register in frontend/src/pages/Home.tsx

**Checkpoint**: Authenticated users keep durable history and receive migrated guest items consistently.

---

## Phase 5: User Story 3 - Clear Guest History Expectations (Priority: P3)

**Goal**: Guest users see explicit temporary-history messaging and a guest-only session history view with predictable session-loss behavior.

**Independent Test**: In guest mode, open history and verify only session items are shown with clear temporary-history messaging before and after session reset.

### Tests for User Story 3

- [ ] T039 [P] [US3] Add backend integration test for guest history context metadata in backend/tests/integration/test_guest_history_metadata.py
- [ ] T040 [P] [US3] Add Playwright scenario for multi-tab guest history consistency in frontend/tests/e2e/guest-history-multitab.spec.ts
- [ ] T041 [P] [US3] Add Playwright scenario for session-end history clearing message in frontend/tests/e2e/guest-history-session-end.spec.ts

### Implementation for User Story 3

- [ ] T042 [US3] Add guest-aware history response metadata in backend/src/schemas/video.py
- [ ] T043 [US3] Return guest history context indicator from list endpoint in backend/src/api/v1/videos.py
- [ ] T044 [US3] Remove unauthenticated redirect and support guest history mode in frontend/src/pages/History.tsx
- [ ] T045 [US3] Render guest-only session history messaging and post-session informational state in frontend/src/components/VideoList.tsx

**Checkpoint**: Guest history behavior is clear, session-scoped, and consistent across tabs and session boundaries.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final quality gates, performance verification, and documentation updates.

- [ ] T046 [P] Add contract coverage for 401 guest-context failures in backend/tests/contract/test_guest_auth_failures_contract.py
- [ ] T047 [P] Benchmark p95 latency for guest and authenticated submit/list/detail endpoints in backend/tests/performance/test_guest_history_latency.py
- [ ] T048 [P] Document performance benchmark results and bottlenecks in specs/002-guest-mode-access/quickstart.md
- [ ] T049 [P] Update API documentation for guest session and migration flows in docs/api.md
- [ ] T050 [P] Update user-facing guest-mode behavior and troubleshooting in docs/user-guide.md
- [ ] T051 Run end-to-end scenario validation from specs/002-guest-mode-access/quickstart.md in specs/002-guest-mode-access/quickstart.md

---

## Dependencies and Execution Order

### Phase Dependencies

- Setup (Phase 1): can start immediately.
- Foundational (Phase 2): depends on Setup and blocks all user story work.
- User Story phases (Phase 3 to Phase 5): all depend on Phase 2 completion.
- Polish (Phase 6): depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): starts after Foundational and delivers MVP guest functionality.
- US2 (P2): starts after Foundational and depends on stable ownership paths from US1.
- US3 (P3): starts after Foundational and can run in parallel with US2 after US1 guest endpoints are stable.

### Within-Story Ordering

- Test tasks for each story are executed first and must fail before implementation.
- Backend models and ownership rules before API behavior changes.
- API behavior changes before frontend integration and messaging updates.

---

## Parallel Execution Examples

### User Story 1

- Run T014, T015, T016, T017, and T018 in parallel before implementation tasks T019 to T028.

### User Story 2

- Run T029, T030, T031, and T032 in parallel before implementation tasks T033 to T038.

### User Story 3

- Run T039, T040, and T041 in parallel before implementation tasks T042 to T045.

---

## Implementation Strategy

### MVP First

1. Finish Phase 1 and Phase 2.
2. Complete US1 in Phase 3.
3. Run US1 contract and integration tests plus a focused quickstart validation.

### Incremental Delivery

1. Ship US1 for immediate guest-access value.
2. Add US2 migration and authenticated continuity.
3. Add US3 history clarity and session-bound UX messaging.
4. Complete Phase 6 quality gates, performance checks, and documentation.
