# Research: Video Transcription & Summarization

**Feature**: Video Transcription & Summarization  
**Date**: 2026-05-21  
**Purpose**: Validate technical choices and resolve architectural decisions

## Research Areas

### 1. Video Extraction & Audio Processing

**Decision**: Use yt-dlp for video/audio extraction

**Rationale**:
- Industry-standard tool with active maintenance (10k+ commits)
- Supports YouTube, Vimeo, 1000+ other platforms
- Handles rate limiting, geo-restrictions automatically
- Python library integration via `yt-dlp` package
- Extracts audio in multiple formats (m4a, webm, mp3)

**Alternatives Considered**:
- **pytube**: Less reliable, frequently breaks with YouTube updates
- **youtube-dl**: Original project less actively maintained than yt-dlp fork
- **Direct API calls**: YouTube API has quota limits, doesn't support all platforms

**Best Practices**:
- Extract audio-only (faster, smaller files): `ydl_opts = {'format': 'bestaudio/best'}`
- Use temporary file storage, cleanup after transcription
- Implement retry logic for transient failures
- Cache extraction metadata to avoid re-downloads

---

### 2. Transcription Service Selection

**Decision**: OpenAI Whisper API for transcription

**Rationale**:
- State-of-the-art accuracy (Word Error Rate: ~5% for English)
- Multi-language support (99 languages)
- Speaker detection capability
- Timestamp granularity to word level
- Managed service (no model hosting required)
- Pricing: $0.006/minute (~$0.36 for 1-hour video)

**Alternatives Considered**:
- **AssemblyAI**: Similar accuracy, slightly higher cost ($0.00025/sec = $0.015/min)
- **Google Cloud Speech-to-Text**: Good accuracy but more complex setup
- **AWS Transcribe**: Longer processing times, less accurate for technical content
- **Self-hosted Whisper**: Requires GPU infrastructure, maintenance overhead

**Best Practices**:
- Use Whisper `large-v3` model for best accuracy
- Request word-level timestamps for highlight extraction
- Implement chunking for videos >25MB (Whisper file size limit)
- Use language detection or allow user language specification
- Store raw API response for future re-processing

---

### 3. AI Summarization Strategy

**Decision**: OpenAI GPT-4 Turbo for summarization and highlight extraction

**Rationale**:
- Long context window (128k tokens = ~96k words)
- Can process full 3-hour video transcript in single call
- Superior quality for abstractive summarization
- Function calling for structured highlight extraction
- Cost-effective: $0.01/1k input tokens, $0.03/1k output tokens

**Alternatives Considered**:
- **Claude 3.5 Sonnet**: Excellent quality, similar pricing, 200k context
- **Llama 3 70B**: Lower quality, would require self-hosting
- **Extractive summarization**: Fast but lower quality than LLM-based

**Best Practices**:
- Use structured prompts with clear instructions
- Request JSON output for highlights (timestamp, text, importance score)
- Implement prompt templates for different summary lengths (brief/medium/detailed)
- Add context about video domain/topic for better results
- Cache summaries with hash of (transcript + prompt template) as key

**Prompt Strategy**:
```
System: You are an expert at analyzing video transcripts and extracting key insights.
User: Analyze this transcript and provide:
1. A concise summary (150 words) covering main points
2. 5-10 key highlights with timestamps, ordered by importance
Format highlights as JSON: [{timestamp, text, importance_score, category}]
```

---

### 4. Async Task Processing Architecture

**Decision**: Celery with Redis as message broker and result backend

**Rationale**:
- Battle-tested async task queue for Python
- Redis provides fast message passing and result storage
- Supports task chaining (extract → transcribe → summarize)
- Built-in retry logic and error handling
- Monitoring via Flower dashboard
- Horizontal scaling: add more workers for increased load

**Alternatives Considered**:
- **RQ (Redis Queue)**: Simpler but fewer features (no task chaining)
- **Dramatiq**: Good alternative but smaller ecosystem
- **FastAPI background tasks**: Too basic for long-running operations

**Best Practices**:
- Separate queues by priority: `transcription` (high), `summarization` (medium)
- Set task timeouts: 10 min for transcription, 2 min for summarization
- Use `task.apply_async()` with `countdown` for rate limit backoff
- Implement progress callbacks via WebSocket
- Store task IDs in database for status tracking

**Task Chain Example**:
```python
chain(
    extract_video.s(video_url),
    transcribe_audio.s(),
    generate_summary.s(),
    extract_highlights.s()
).apply_async()
```

---

### 5. Real-Time Progress Updates

**Decision**: WebSocket for progress updates, REST API for everything else

**Rationale**:
- WebSocket provides instant bidirectional communication
- Ideal for long-running task progress (transcription, summarization)
- FastAPI has built-in WebSocket support
- Avoids polling overhead and reduces server load
- Automatic reconnection handling on client side

**Alternatives Considered**:
- **Server-Sent Events (SSE)**: One-way only, less browser support
- **HTTP polling**: High latency, wasteful, poor UX
- **Long polling**: Better than polling but still inefficient

**Best Practices**:
- WebSocket endpoint: `/ws/{video_id}` for per-video updates
- Send structured messages: `{event: 'progress', stage: 'transcription', percent: 45}`
- Implement ping/pong for connection health checks
- Fall back to REST API polling if WebSocket fails
- Close connections after task completion to free resources

**Event Types**:
```typescript
type ProgressEvent = {
  event: 'progress'
  stage: 'extracting' | 'transcribing' | 'summarizing'
  percent: number
  message: string
}

type CompletionEvent = {
  event: 'complete'
  video_id: string
  transcription_id: string
  summary_id: string
}
```

---

### 6. Database Schema Design

**Decision**: PostgreSQL with normalized schema + JSONB for flexible data

**Rationale**:
- ACID compliance for data integrity
- JSONB type perfect for storing transcript segments (variable structure)
- Full-text search capabilities for transcript search
- Indexing on JSONB fields for fast queries
- JSON aggregation for complex queries

**Alternatives Considered**:
- **MongoDB**: Good for JSON but weaker consistency guarantees
- **SQLite**: Not suitable for concurrent access in production
- **Pure JSON columns**: Could work but loses referential integrity

**Schema Design**:
```sql
-- Core entities
users (id, email, created_at)
videos (id, user_id, url, platform, duration, status, created_at)
transcriptions (id, video_id, language, segments JSONB, created_at)
summaries (id, transcription_id, summary_length, content TEXT, created_at)
highlights (id, summary_id, timestamp, text, importance_score, category)
shareable_links (id, video_id, timestamp, token, expires_at, created_at)

-- Indexes
CREATE INDEX idx_transcriptions_video ON transcriptions(video_id);
CREATE INDEX idx_segments_gin ON transcriptions USING GIN (segments);
CREATE INDEX idx_highlights_timestamp ON highlights(timestamp);
CREATE INDEX idx_shareable_token ON shareable_links(token);
```

**JSONB Segment Structure**:
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Welcome to this tutorial",
      "speaker": "speaker_1"
    }
  ]
}
```

---

### 7. Caching Strategy

**Decision**: Multi-layer caching with Redis and in-memory cache

**Rationale**:
- Redis: Cache transcriptions (expensive), summaries, extraction metadata
- In-memory (Python functools.lru_cache): User preferences, config
- CDN: Static frontend assets
- Significant cost savings by avoiding re-transcription

**Cache Policy**:
- **Transcriptions**: 7 days TTL, keyed by video URL hash
- **Summaries**: 7 days TTL, keyed by (transcription_id + summary_params)
- **Highlights**: 7 days TTL, tied to summary cache
- **Video metadata**: 24 hours TTL
- **User history**: No cache (read from DB for accuracy)

**Best Practices**:
- Implement cache warming for popular videos
- Use Redis SET with EX for automatic expiration
- Add cache versioning for schema changes: `v1:transcript:{hash}`
- Monitor cache hit rates (target: >80%)
- Implement cache stampede prevention with locks

---

### 8. Frontend Performance Optimization

**Decision**: React with code-splitting, lazy loading, and optimistic updates

**Rationale**:
- **Code-splitting**: Load routes on-demand (React.lazy + Suspense)
- **TanStack Query**: Automatic caching, deduplication, background refetching
- **Virtual scrolling**: For long transcripts (react-window)
- **Optimistic updates**: Instant UI feedback, rollback on error
- **Service worker**: Cache API responses, offline support

**Bundle Size Targets**:
- Initial bundle: <100KB gzipped
- Per-route chunks: <50KB gzipped
- Total JavaScript: <300KB gzipped

**Performance Metrics**:
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1

**Best Practices**:
- Use React.memo for expensive components
- Debounce search input (300ms)
- Implement infinite scroll for history page
- Preload critical data on hover
- Use Tailwind CSS for minimal CSS bundle

---

### 9. Error Handling & Resilience

**Decision**: Structured error codes with retry logic and circuit breakers

**Error Code System**:
```
VID-001: Invalid video URL format
VID-002: Video not accessible (private/deleted)
VID-003: Video too long (>3 hours)
VID-004: Unsupported platform
TRN-001: Transcription service unavailable
TRN-002: Audio quality too poor
TRN-003: Transcription timeout
SUM-001: Summarization failed
SUM-002: Transcript too short for summary
```

**Resilience Patterns**:
- **Retry with exponential backoff**: 3 attempts for API calls
- **Circuit breaker**: Stop calling failing services after 5 failures
- **Graceful degradation**: Show partial results if summarization fails
- **Timeout handling**: 10-min max for transcription, 2-min for summarization

**Best Practices**:
- Log all errors with context (video_id, user_id, task_id)
- Return actionable error messages to users
- Implement dead letter queue for failed tasks
- Monitor error rates and alert on spikes

---

### 10. Security Considerations

**Authentication**: JWT tokens with 24-hour expiration

**Rate Limiting**: 
- API: 100 requests/min per user
- Video submission: 10 videos/hour per user
- Enforce at API gateway level (FastAPI middleware)

**Input Validation**:
- Validate URL format and domain allowlist
- Sanitize all user inputs (XSS prevention)
- Limit video duration (3 hours max)
- File size validation for uploads

**Data Security**:
- Encrypt sensitive data at rest
- Use environment variables for API keys
- Implement CORS properly
- SQL injection protection via SQLAlchemy ORM

---

## Technology Stack Summary

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Backend Language | Python | 3.11+ | Constitution requirement, excellent AI/ML libraries |
| API Framework | FastAPI | 0.104+ | Async, type-safe, auto-docs, high performance |
| Frontend Framework | React | 18+ | Industry standard, rich ecosystem, fast |
| Frontend Language | TypeScript | 5.0+ | Type safety, better DX, fewer runtime errors |
| Database | PostgreSQL | 15+ | JSONB support, full-text search, reliability |
| Cache/Queue | Redis | 7+ | Fast, versatile (cache + message broker) |
| Task Queue | Celery | 5.3+ | Mature, scalable async processing |
| Transcription | OpenAI Whisper | API | Best accuracy, managed service |
| Summarization | GPT-4 Turbo | API | Long context, high quality |
| Video Extraction | yt-dlp | Latest | Multi-platform, reliable |
| Testing (Backend) | pytest | 7+ | Constitution requirement, comprehensive |
| Testing (Frontend) | Vitest | 1+ | Fast, Vite-native, compatible with Jest |
| Linting (Backend) | ruff | 0.1+ | Fast, comprehensive, Python-native |
| Linting (Frontend) | ESLint | 8+ | Industry standard, extensive rules |
| Type Checking | mypy / tsc | Latest | Constitution requirement |

---

## Open Questions / Future Considerations

None - all technical decisions validated and documented.