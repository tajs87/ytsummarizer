# Implementation Plan: Guest Mode Access

**Branch**: `002-video-transcription-summary` | **Date**: 2026-05-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-guest-mode-access/spec.md`

## Summary

Add a first-class guest mode that allows users to submit videos, view transcription/summaries, and view a current-session guest history without creating an account. Guest identity will be tracked by a server-issued anonymous session token in a secure httpOnly cookie. On sign-in/registration, all current-session guest items are automatically migrated to authenticated account history.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, Alembic, Celery, Redis, Pydantic settings
- Frontend: React 18, TanStack Query, React Router, TypeScript strict mode

**Storage**: PostgreSQL (persistent video/transcription/summary data), Redis (queue/cache), cookie-based guest session token

**Testing**: pytest + pytest-asyncio (backend), Vitest + React Testing Library (frontend), Playwright E2E

**Target Platform**: Docker-based web app (backend API + worker + frontend)

**Project Type**: Full-stack web application

**Performance Goals**:
- Guest/authenticated submit/list/detail endpoints: <200ms p95 metadata operations
- No degradation relative to existing transcription pipeline throughput

**Constraints**:
- Guest history is session-only
- Automatic migration of all current-session guest items at successful authentication
- Maintain existing authenticated history semantics

**Scale/Scope**:
- One new feature vertical across backend auth/video APIs, frontend auth/history UX, and migration flow
- Initial target: existing development scale (single-node compose) with multi-user correctness

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability

- PASS: Feature can be introduced through focused API/service/model changes with explicit typing and error handling.

### II. Testing Standards & Coverage (NON-NEGOTIABLE)

- PASS: Plan includes unit/integration/contract coverage for guest session identification, history visibility, and migration behavior.

### III. User Experience Consistency

- PASS: Guest vs authenticated behavior is explicit, with predictable history rules and clear UI messaging.

### IV. Performance & Efficiency

- PASS: Adds lightweight session-token checks and ownership reassignment at login, preserving async processing architecture.

**Gate Result**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/002-guest-mode-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/v1/
│   ├── models/
│   ├── services/
│   └── db/migrations/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Use existing web app split (`backend/` + `frontend/`) and add guest-mode behavior within current auth/video/history flows rather than introducing a parallel application path.

## Complexity Tracking

No constitution violations requiring exception.

## Post-Design Constitution Check

### I. Code Quality & Maintainability

- PASS: Data model and contracts keep guest semantics explicit and bounded.

### II. Testing Standards & Coverage

- PASS: Quickstart and design artifacts include scenario coverage for guest-only session behavior and migration.

### III. User Experience Consistency

- PASS: Guest history messaging and behavior are consistently defined.

### IV. Performance & Efficiency

- PASS: Session-token approach and migration are compatible with existing architecture and scale constraints.

**Post-Design Gate Result**: PASS
