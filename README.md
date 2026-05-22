# YTSum: Video Transcription & Summarization

YTSum is a full-stack web application that transcribes videos, generates AI-powered summaries, and creates shareable timestamp links.

## Features

- Video transcription for YouTube, Vimeo, and direct video URLs
- Searchable full-text transcription with timestamps
- Export transcription as TXT, CSV, or JSON
- AI summaries (brief, detailed, bullet points)
- Highlight extraction for key moments
- Shareable timestamp links
- Real-time progress updates via WebSocket

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL
- Frontend: React, TypeScript, Vite, TanStack Query, Tailwind CSS
- AI: OpenAI Whisper (transcription), GPT-based summaries
- Infrastructure: Docker Compose

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- OpenAI API key with available credits

### 2. Configure Environment

Create or update `.env` in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
```

### 3. Start Services

```bash
docker-compose up -d
```

Services:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 4. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

## Development

### Backend

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests

```bash
cd backend
uv run pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## Documentation

- API docs: `docs/api.md`
- User guide: `docs/user-guide.md`
- Feature spec: `specs/001-video-transcription-summary/spec.md`

## Current Status

- Phase 1: Setup infrastructure - Complete
- Phase 2: Foundation components - Complete
- Phase 3: Basic Transcription (MVP) - In progress
- Phase 4: Summarization - Implemented
- Phase 5: Sharing - Implemented
- Phase 6: Multi-platform - Implemented
- Phase 7: Polish - In progress
