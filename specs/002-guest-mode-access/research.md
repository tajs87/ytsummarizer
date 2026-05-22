# Research: Guest Mode Access

## Decision 1: Guest identity mechanism
- Decision: Use a server-issued anonymous session token stored in a secure httpOnly cookie.
- Rationale: Supports cross-tab continuity, reduces client-side tampering risk, and aligns with requirement FR-012.
- Alternatives considered:
  - localStorage token: easier client access but weaker security and easier mutation.
  - in-memory tab token: safest ephemeral behavior but breaks cross-tab consistency.
  - IP/user-agent fingerprint: unreliable and privacy-risky.

## Decision 2: Guest history scope
- Decision: Maintain guest history only for active session and clear it when session ends.
- Rationale: Directly matches clarified requirement and user expectation of "no account = no persistent history".
- Alternatives considered:
  - Persist guest history locally beyond session: conflicts with clarified behavior.
  - Server-side TTL guest retention: adds complexity and expectation mismatch.

## Decision 3: API surface strategy
- Decision: Keep core video submit/detail flows available to both guest and authenticated contexts; provide explicit guest-session/history behavior in API contracts.
- Rationale: Minimizes frontend duplication and keeps behavior consistent.
- Alternatives considered:
  - Entirely separate guest endpoints for all operations: higher maintenance cost and potential divergence.

## Decision 4: Migration behavior at authentication
- Decision: Automatically migrate all current-session guest items to authenticated account history upon successful sign-in/registration.
- Rationale: Explicitly chosen during clarification; preserves user work and reduces friction.
- Alternatives considered:
  - Prompt-per-item migration: more UX complexity.
  - No migration: rejected by clarification outcome.

## Decision 5: Data ownership model
- Decision: Represent ownership context so entries are attributable to either guest session or authenticated user, with deterministic reassignment on migration.
- Rationale: Required for correctness of list/filter/history and secure access control.
- Alternatives considered:
  - Duplicate records on migration: risks data drift and duplicate processing semantics.
  - Opaque unowned records: difficult to authorize and audit.

## Decision 6: Failure handling for migration
- Decision: Perform migration as an atomic backend operation at authentication success boundary.
- Rationale: Prevents partial ownership transfer and inconsistent history states.
- Alternatives considered:
  - Background migration after login response: can produce temporary mismatch in UI/history.
