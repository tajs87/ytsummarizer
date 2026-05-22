# Data Model: Video Transcription & Summarization

**Feature**: Video Transcription & Summarization  
**Date**: 2026-05-21  
**Purpose**: Define core entities, relationships, and data structures

## Entity Overview

```
User ──< Video ──< Transcription ──< Summary ──< Highlight
                │
                └──< ShareableLink
```

## Core Entities

### User

Represents a registered user of the system.

**Attributes**:
- `id` (UUID): Unique identifier
- `email` (string, unique): User email address for authentication
- `username` (string, unique): Display name
- `password_hash` (string): Bcrypt hashed password
- `created_at` (timestamp): Account creation time
- `last_login` (timestamp): Most recent login
- `is_active` (boolean): Account status (for soft deletes)
- `rate_limit_tokens` (integer): Remaining API tokens for current period

**Validation Rules**:
- Email must be valid format and unique
- Password minimum 8 characters with complexity requirements
- Username 3-30 characters, alphanumeric + underscore

**Relationships**:
- One user has many videos (1:N)

---

### Video

Represents a video submitted for processing.

**Attributes**:
- `id` (UUID): Unique identifier
- `user_id` (UUID, foreign key): Owner of this video request
- `url` (string, unique): Original video URL
- `url_hash` (string, indexed): SHA-256 hash of URL (for cache lookups)
- `platform` (enum): Source platform (youtube, vimeo, direct, other)
- `title` (string, nullable): Video title (extracted from metadata)
- `duration_seconds` (integer, nullable): Video length
- `thumbnail_url` (string, nullable): Video thumbnail
- `status` (enum): Processing state (see Status States below)
- `error_code` (string, nullable): Error identifier if failed (e.g., "VID-002")
- `error_message` (string, nullable): Human-readable error description
- `metadata` (JSONB): Additional platform-specific metadata
- `created_at` (timestamp): Submission time
- `updated_at` (timestamp): Last status change
- `completed_at` (timestamp, nullable): Processing completion time

**Status States**:
- `submitted`: Initial state, queued for extraction
- `extracting`: Downloading video/audio
- `extracted`: Audio ready for transcription
- `transcribing`: Transcription in progress
- `transcribed`: Transcription complete, ready for summarization
- `summarizing`: Summary generation in progress
- `completed`: Fully processed and ready
- `failed`: Processing error occurred

**Validation Rules**:
- URL must be valid HTTP/HTTPS format
- Duration must be ≤10,800 seconds (3 hours)
- Platform must be supported (validated against allowlist)
- Status transitions must follow state machine logic

**Relationships**:
- Belongs to one user (N:1)
- Has one transcription (1:1, nullable)
- Has many shareable links (1:N)

**Indexes**:
- `url_hash` (for duplicate detection)
- `user_id, created_at` (for user history queries)
- `status` (for monitoring)

---

### Transcription

Contains the full text transcription with timing information.

**Attributes**:
- `id` (UUID): Unique identifier
- `video_id` (UUID, foreign key, unique): Associated video
- `language` (string): Detected/specified language code (ISO 639-1)
- `duration_seconds` (integer): Total audio duration
- `word_count` (integer): Total words in transcript
- `segments` (JSONB): Array of transcript segments with timestamps
- `full_text` (text): Complete transcript (for full-text search)
- `confidence_score` (float): Average transcription confidence (0-1)
- `processing_time_seconds` (integer): Time taken to transcribe
- `model_version` (string): Transcription model identifier (e.g., "whisper-large-v3")
- `created_at` (timestamp): Transcription completion time

**Segment Structure** (JSONB):
```json
{
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.23,
      "text": "Welcome to this tutorial on video transcription.",
      "words": [
        {"word": "Welcome", "start": 0.0, "end": 0.5, "confidence": 0.98}
      ],
      "speaker": "speaker_1",
      "confidence": 0.96
    }
  ]
}
```

**Validation Rules**:
- Language must be valid ISO 639-1 code
- Segments must have sequential, non-overlapping timestamps
- Confidence score between 0.0 and 1.0
- full_text derived from segments (denormalized for search)

**Relationships**:
- Belongs to one video (N:1)
- Has many summaries (1:N)

**Indexes**:
- `video_id` (unique, for fast lookups)
- Full-text index on `full_text` (for search)
- GIN index on `segments` JSONB (for JSON queries)

---

### Summary

AI-generated summary of the transcription.

**Attributes**:
- `id` (UUID): Unique identifier
- `transcription_id` (UUID, foreign key): Source transcription
- `summary_type` (enum): Length/detail level (brief, medium, detailed)
- `content` (text): Summary text
- `word_count` (integer): Summary length
- `compression_ratio` (float): Summary length / original length
- `main_topics` (array of strings): Extracted key topics/themes
- `model_version` (string): AI model used (e.g., "gpt-4-turbo")
- `prompt_template_version` (string): Prompt version for cache invalidation
- `processing_time_seconds` (integer): Generation time
- `created_at` (timestamp): Summary creation time

**Summary Types**:
- `brief`: ~150 words, high-level overview
- `medium`: ~300 words, balanced detail
- `detailed`: ~500 words, comprehensive analysis

**Validation Rules**:
- content must not be empty
- word_count must match actual word count
- compression_ratio = summary_words / transcript_words
- main_topics max 10 items

**Relationships**:
- Belongs to one transcription (N:1)
- Has many highlights (1:N)

**Indexes**:
- `transcription_id, summary_type` (composite, for caching)

---

### Highlight

Individual key point or important moment extracted from the transcription.

**Attributes**:
- `id` (UUID): Unique identifier
- `summary_id` (UUID, foreign key): Parent summary
- `timestamp_start` (float): Start time in seconds
- `timestamp_end` (float): End time in seconds
- `text` (text): Highlight content (excerpt from transcript)
- `importance_score` (float): AI-assigned importance (0-1, higher = more important)
- `category` (string): Classification (definition, action_item, key_insight, example, conclusion)
- `context_before` (text, nullable): Brief context preceding the highlight
- `context_after` (text, nullable): Brief context following the highlight
- `created_at` (timestamp): Extraction time

**Validation Rules**:
- timestamp_end must be > timestamp_start
- importance_score between 0.0 and 1.0
- text must not be empty
- category must be from predefined list

**Relationships**:
- Belongs to one summary (N:1)

**Indexes**:
- `summary_id, importance_score DESC` (for ordered retrieval)
- `timestamp_start` (for timeline queries)

---

### ShareableLink

Generated links for sharing specific video moments.

**Attributes**:
- `id` (UUID): Unique identifier
- `video_id` (UUID, foreign key): Associated video
- `token` (string, unique, indexed): Short URL token (e.g., "abc123")
- `timestamp` (float): Video position in seconds
- `duration` (integer, nullable): Clip duration (if sharing a range)
- `title` (string, nullable): Custom title for the shared moment
- `description` (text, nullable): Context/notes about this moment
- `view_count` (integer): Number of times accessed
- `created_by` (UUID, foreign key): User who created link
- `created_at` (timestamp): Link creation time
- `expires_at` (timestamp, nullable): Optional expiration date
- `is_active` (boolean): Enabled/disabled status

**Validation Rules**:
- token must be unique, 8-12 alphanumeric characters
- timestamp must be within video duration
- expires_at must be in the future if set
- duration must be positive if set

**Relationships**:
- Belongs to one video (N:1)
- Created by one user (N:1)

**Indexes**:
- `token` (unique, for fast lookups)
- `video_id` (for video-specific links)
- `expires_at` (for cleanup queries)

---

## State Transitions

### Video Processing State Machine

```
submitted → extracting → extracted → transcribing → transcribed → summarizing → completed
     ↓           ↓           ↓            ↓             ↓              ↓
   failed      failed      failed       failed        failed        failed
```

**Transition Rules**:
- Can only move forward through states (except to failed)
- Failed state is terminal (requires new video submission)
- Each state has maximum timeout:
  - extracting: 5 minutes
  - transcribing: 10 minutes  
  - summarizing: 2 minutes

---

## Derived Data & Caching

### Cache Keys

**Transcription Cache**:
- Key: `v1:transcript:{url_hash}`
- TTL: 7 days
- Value: Complete transcription JSON

**Summary Cache**:
- Key: `v1:summary:{transcription_id}:{summary_type}:{prompt_version}`
- TTL: 7 days
- Value: Summary + highlights JSON

**Video Metadata Cache**:
- Key: `v1:video_meta:{url_hash}`
- TTL: 24 hours
- Value: Title, duration, thumbnail

### Computed Fields

**Video**:
- `processing_duration` = `completed_at - created_at` (computed on query)

**Transcription**:
- `full_text` = concatenated segment text (stored for search)
- `average_confidence` = mean of segment confidence scores

**Summary**:
- `compression_ratio` = `summary_word_count / transcript_word_count`

---

## Data Retention Policy

- **Active videos**: Retained indefinitely
- **Failed videos**: Retained 7 days for debugging
- **Transcriptions**: Retained 30 days minimum
- **Summaries/Highlights**: Tied to transcription lifecycle
- **Shareable links**: Expired links deleted after 30 days
- **User data**: Soft delete (is_active=false), hard delete after 90 days

---

## Search Capabilities

### Full-Text Search

Implemented on `transcriptions.full_text` using PostgreSQL full-text search:

```sql
CREATE INDEX idx_transcription_search ON transcriptions 
USING GIN (to_tsvector('english', full_text));
```

**Search Features**:
- Exact phrase search
- Fuzzy matching
- Ranked results by relevance
- Highlight matching terms in results

### Timestamp Search

Find highlights within a time range:

```sql
SELECT * FROM highlights 
WHERE summary_id = ? 
AND timestamp_start BETWEEN ? AND ?
ORDER BY importance_score DESC;
```

---

## Performance Considerations

**Hot Paths** (optimize with indexes):
- User video history: `SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC`
- Get transcription for video: `SELECT * FROM transcriptions WHERE video_id = ?`
- Find cached transcription: Cache lookup by `url_hash` before DB
- Shareable link lookup: `SELECT * FROM shareable_links WHERE token = ? AND is_active = true`

**Cold Paths** (acceptable to be slower):
- Admin analytics queries
- Batch cleanup of expired links
- Historical data exports

**Optimization Strategies**:
- Partial indexes on `status` for active processing videos
- Materialized view for popular videos (view_count > 100)
- Partition large tables by created_at (monthly partitions)
- Archive old transcriptions to cold storage after 90 days

---

## Data Integrity Constraints

**Database Level**:
- Foreign key constraints with `ON DELETE CASCADE` for orphan prevention
- Unique constraints on `users.email`, `videos.url`, `shareable_links.token`
- Check constraints: `duration_seconds > 0`, `importance_score BETWEEN 0 AND 1`
- NOT NULL on critical fields: `id`, `created_at`, `status`

**Application Level**:
- Validate state transitions before updates
- Atomic operations for multi-table updates (use transactions)
- Retry logic for transient failures
- Idempotency keys for duplicate request prevention

---

## Migration Strategy

**Initial Schema**:
- Create all tables with indexes
- Seed with platform allowlist data
- Create database functions for common queries

**Future Migrations**:
- Use Alembic for version control
- Zero-downtime migrations (add columns, backfill, remove old)
- Test migrations on staging with production data copy
- Rollback plan for each migration

---

## Summary

Designed 6 core entities with clear relationships, comprehensive validation rules, and optimized indexing strategy. JSONB used for flexible transcript storage enables future format changes without schema migrations. Caching strategy at multiple layers (Redis, application) ensures performance targets met. State machine approach for video processing provides clear visibility and error recovery.