# Quickstart Guide: Video Transcription & Summarization

**Feature**: Video Transcription & Summarization  
**Date**: 2026-05-21  
**Target Audience**: Developers setting up local development environment

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Docker**: 24+ with Docker Compose
- **PostgreSQL**: 15+ (or use Docker)
- **Redis**: 7+ (or use Docker)
- **uv**: Python package installer (recommended) or pip
- **Git**: For version control

## Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd ytsum
```

### 2. Start Infrastructure (Docker)

Start PostgreSQL and Redis using Docker Compose:

```bash
docker-compose up -d postgres redis
```

Verify services are running:

```bash
docker-compose ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY (for Whisper and GPT-4)
# - DATABASE_URL (default: postgresql://postgres:password@localhost:5432/ytsum)
# - REDIS_URL (default: redis://localhost:6379/0)

# Run database migrations
alembic upgrade head

# Start FastAPI server (with auto-reload)
uvicorn src.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### 4. Start Celery Worker (Separate Terminal)

```bash
cd backend
source .venv/bin/activate
celery -A src.tasks.app worker --loglevel=info
```

### 5. Frontend Setup (Separate Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env:
# VITE_API_URL=http://localhost:8000/api/v1
# VITE_WS_URL=ws://localhost:8000/api/v1

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## Verify Installation

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "celery": "running"
}
```

### 2. Create Test User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### 3. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

Save the `access_token` from the response.

### 4. Submit Test Video

```bash
export TOKEN="<your-access-token>"

curl -X POST http://localhost:8000/api/v1/videos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

### 5. Monitor Progress

Open the frontend at `http://localhost:5173` and watch the real-time progress updates!

---

## Development Workflow

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest                        # Run all tests
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest --cov=src             # With coverage report
```

**Frontend Tests**:
```bash
cd frontend
npm test                     # Run all tests
npm run test:watch          # Watch mode
npm run test:coverage       # With coverage
```

### Code Quality Checks

**Backend**:
```bash
cd backend
ruff check src/             # Linting
ruff format src/            # Formatting
mypy src/                   # Type checking
```

**Frontend**:
```bash
cd frontend
npm run lint                # ESLint
npm run format              # Prettier
npm run type-check         # TypeScript check
```

### Database Migrations

**Create New Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add user preferences table"
```

**Apply Migrations**:
```bash
alembic upgrade head
```

**Rollback**:
```bash
alembic downgrade -1  # Rollback one migration
```

---

## Architecture Overview

### Request Flow

```
User Browser → React App → FastAPI REST API → Celery Task Queue
                    ↓                              ↓
                WebSocket ← Status Updates ← Redis + Workers
                                                   ↓
                                            PostgreSQL
```

### Processing Pipeline

```
1. Video URL Submitted
   ↓
2. Celery Task: extract_video (yt-dlp)
   ↓
3. Celery Task: transcribe_audio (OpenAI Whisper)
   ↓
4. Celery Task: generate_summary (GPT-4)
   ↓
5. Store Results in PostgreSQL
   ↓
6. Notify Client via WebSocket
```

### Key Components

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| Frontend | React + TypeScript | 5173 | User interface |
| Backend API | FastAPI | 8000 | REST endpoints |
| Worker | Celery + Python | - | Async tasks |
| Database | PostgreSQL | 5432 | Persistent storage |
| Cache/Queue | Redis | 6379 | Caching + message broker |

---

## Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# API Keys
OPENAI_API_KEY=sk-...                # Required for Whisper + GPT-4

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ytsum

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here      # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440         # 24 hours

# Rate Limiting
RATE_LIMIT_VIDEOS_PER_HOUR=10
RATE_LIMIT_API_PER_MINUTE=100

# Video Processing
MAX_VIDEO_DURATION_SECONDS=10800    # 3 hours
VIDEO_TEMP_DIR=/tmp/ytsum

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1
VITE_APP_NAME=YTSummarizer
```

---

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError`  
**Solution**: Ensure virtual environment activated and dependencies installed
```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Problem**: Database connection error  
**Solution**: Verify PostgreSQL is running and credentials are correct
```bash
docker-compose ps
psql postgresql://postgres:password@localhost:5432/ytsum -c '\l'
```

### Celery Worker Issues

**Problem**: Tasks not processing  
**Solution**: Check Celery worker is running and connected to Redis
```bash
celery -A src.tasks.app inspect active
```

**Problem**: `OpenAI API key not found`  
**Solution**: Verify `OPENAI_API_KEY` in `.env` and restart worker

### Frontend Issues

**Problem**: API calls failing (CORS)  
**Solution**: Ensure backend CORS middleware allows `http://localhost:5173`

**Problem**: WebSocket connection fails  
**Solution**: Check browser console for errors, verify WS_URL in frontend `.env`

### Database Migration Issues

**Problem**: `Target database is not up to date`  
**Solution**: Apply pending migrations
```bash
alembic upgrade head
```

**Problem**: Migration conflicts  
**Solution**: Merge migration heads
```bash
alembic merge heads
```

---

## Common Development Tasks

### Add New API Endpoint

1. Define route in `backend/src/api/v1/<module>.py`
2. Add Pydantic schemas in `backend/src/schemas/<module>.py`
3. Implement business logic in `backend/src/services/<module>.py`
4. Write tests in `backend/tests/integration/test_<module>.py`
5. Update OpenAPI contract in `specs/*/contracts/api.yaml`

### Add New React Component

1. Create component in `frontend/src/components/<Component>.tsx`
2. Add types in `frontend/src/types/<module>.ts`
3. Write tests in `frontend/tests/unit/<Component>.test.tsx`
4. Use Storybook for isolated development: `npm run storybook`

### Add New Celery Task

1. Define task in `backend/src/tasks/<module>.py`
2. Register in `backend/src/tasks/__init__.py`
3. Add unit tests in `backend/tests/unit/test_tasks.py`
4. Test with: `celery -A src.tasks.app call src.tasks.transcribe --args='["test"]'`

---

## Testing Strategy

### Unit Tests
- Pure functions and utilities
- Service layer business logic
- React component rendering

### Integration Tests
- API endpoint contracts
- Database operations
- External API integrations (mocked)

### End-to-End Tests
- Complete user workflows
- WebSocket communication
- Full processing pipeline

**Run All Tests**:
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test

# E2E (requires running app)
cd frontend && npm run test:e2e
```

---

## Next Steps

1. **Read the Spec**: Review `specs/001-video-transcription-summary/spec.md`
2. **Review Data Model**: Understand entities in `specs/001-video-transcription-summary/data-model.md`
3. **Study API Contracts**: Familiarize with `specs/001-video-transcription-summary/contracts/api.yaml`
4. **Implement User Story 1**: Start with basic transcription (P1 priority)
5. **Write Tests First**: Follow TDD approach per constitution

---

## Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Constitution**: `.specify/memory/constitution.md`
- **Research**: `specs/001-video-transcription-summary/research.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Celery Docs**: https://docs.celeryproject.org/

---

## Support

For questions or issues:
1. Check `specs/001-video-transcription-summary/research.md` for technical decisions
2. Review constitution at `.specify/memory/constitution.md` for standards
3. Consult team documentation in project wiki
4. Create issue in project tracker with reproduction steps

---

**Happy Coding! 🚀**