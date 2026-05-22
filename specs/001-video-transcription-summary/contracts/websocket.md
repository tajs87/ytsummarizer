# WebSocket Event Contracts

**Feature**: Video Transcription & Summarization  
**Protocol**: WebSocket (RFC 6455)  
**Date**: 2026-05-21

## Overview

WebSocket connections provide real-time progress updates for long-running video processing operations. Clients establish a persistent connection to receive status updates without polling.

## Connection

### Endpoint

```
ws://localhost:8000/api/v1/ws/{video_id}
wss://api.ytsummarizer.com/v1/ws/{video_id}
```

### Authentication

Include JWT token in query parameter or initial message:

**Option 1: Query Parameter**
```
ws://localhost:8000/api/v1/ws/{video_id}?token={jwt_token}
```

**Option 2: Initial Message**
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Connection Lifecycle

1. Client initiates connection to `/ws/{video_id}`
2. Server validates authentication
3. Server sends initial status message
4. Server sends progress updates as processing advances
5. Connection closes after task completion or client disconnect

### Heartbeat

Server sends ping frames every 30 seconds. Client should respond with pong to maintain connection.

```json
{
  "type": "ping",
  "timestamp": 1716336000000
}
```

Client response:
```json
{
  "type": "pong",
  "timestamp": 1716336000000
}
```

---

## Server-to-Client Events

### 1. Connection Established

Sent immediately after successful authentication.

```json
{
  "type": "connected",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "current_status": "transcribing",
  "timestamp": 1716336000000
}
```

**Fields**:
- `type`: Event type identifier
- `video_id`: UUID of the video being processed
- `current_status`: Current processing state
- `timestamp`: Unix timestamp (milliseconds)

---

### 2. Progress Update

Sent periodically during processing (every 5-10 seconds or on milestone completion).

```json
{
  "type": "progress",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "stage": "transcribing",
  "percent": 45,
  "message": "Transcribing audio (3:45 of 8:20 processed)",
  "timestamp": 1716336030000
}
```

**Fields**:
- `type`: Always "progress"
- `video_id`: Video UUID
- `stage`: Current processing stage (enum: "extracting" | "transcribing" | "summarizing")
- `percent`: Completion percentage (0-100)
- `message`: Human-readable progress description
- `timestamp`: Unix timestamp (milliseconds)

**Stage Progression**:
- `extracting`: Downloading video/audio from source
- `transcribing`: Converting audio to text
- `summarizing`: Generating AI summary and highlights

---

### 3. Stage Completed

Sent when a major processing stage completes successfully.

```json
{
  "type": "stage_complete",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "stage": "transcribing",
  "duration_seconds": 127,
  "next_stage": "summarizing",
  "timestamp": 1716336157000
}
```

**Fields**:
- `type`: Always "stage_complete"
- `video_id`: Video UUID
- `stage`: Completed stage
- `duration_seconds`: Time taken for this stage
- `next_stage`: Next processing stage, or `null` if complete
- `timestamp`: Unix timestamp (milliseconds)

---

### 4. Processing Complete

Sent when all processing is finished successfully.

```json
{
  "type": "complete",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "transcription_id": "987e4567-e89b-12d3-a456-426614174001",
  "summary_id": "456e4567-e89b-12d3-a456-426614174002",
  "total_duration_seconds": 245,
  "timestamp": 1716336245000
}
```

**Fields**:
- `type`: Always "complete"
- `video_id`: Video UUID
- `transcription_id`: Generated transcription UUID
- `summary_id`: Generated summary UUID (if summarization requested)
- `total_duration_seconds`: Total processing time
- `timestamp`: Unix timestamp (milliseconds)

**Post-Completion Actions**:
- Connection remains open for 5 seconds, then closes with code 1000 (normal closure)
- Client can now fetch full results via REST API

---

### 5. Error Event

Sent when processing fails at any stage.

```json
{
  "type": "error",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "error_code": "TRN-001",
  "message": "Transcription service unavailable",
  "detail": "OpenAI API returned 503 Service Unavailable. The video will be retried automatically.",
  "stage": "transcribing",
  "retry_attempt": 2,
  "max_retries": 3,
  "timestamp": 1716336180000
}
```

**Fields**:
- `type`: Always "error"
- `video_id`: Video UUID
- `error_code`: Structured error code (e.g., VID-001, TRN-002)
- `message`: User-friendly error message
- `detail`: Technical details and recovery actions
- `stage`: Stage where error occurred
- `retry_attempt`: Current retry attempt (if applicable)
- `max_retries`: Maximum retry attempts before failure
- `timestamp`: Unix timestamp (milliseconds)

**Error Codes**:
- `VID-001`: Invalid video URL
- `VID-002`: Video not accessible (private/deleted)
- `VID-003`: Video exceeds duration limit
- `VID-004`: Unsupported platform
- `TRN-001`: Transcription service unavailable
- `TRN-002`: Audio quality too poor
- `TRN-003`: Transcription timeout
- `SUM-001`: Summarization failed
- `SUM-002`: Transcript too short for summary

**Recovery Behavior**:
- Transient errors (TRN-001) trigger automatic retry with exponential backoff
- Permanent errors (VID-002, VID-003) close connection with code 1008 (policy violation)
- After max retries exceeded, connection closes with code 1011 (server error)

---

### 6. Warning Event

Sent for non-fatal issues that don't stop processing.

```json
{
  "type": "warning",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "code": "LOW_CONFIDENCE",
  "message": "Low transcription confidence detected",
  "detail": "Audio quality is poor. Transcription accuracy may be reduced. Consider re-recording with clearer audio.",
  "timestamp": 1716336090000
}
```

**Fields**:
- `type`: Always "warning"
- `video_id`: Video UUID
- `code`: Warning code
- `message`: Warning summary
- `detail`: Additional context and recommendations
- `timestamp`: Unix timestamp (milliseconds)

---

## Client-to-Server Events

### 1. Authentication

Send JWT token if not provided in connection URL.

```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**: Server sends `connected` event or closes with code 4001 (unauthorized)

---

### 2. Heartbeat Response

Respond to server ping to keep connection alive.

```json
{
  "type": "pong",
  "timestamp": 1716336000000
}
```

---

### 3. Cancel Processing (Optional)

Request to cancel ongoing processing.

```json
{
  "type": "cancel",
  "video_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response**:
```json
{
  "type": "cancelled",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": 1716336120000
}
```

Connection closes with code 1000 (normal closure) after confirmation.

---

## Connection Close Codes

Standard WebSocket close codes plus custom application codes:

| Code | Name | Description |
|------|------|-------------|
| 1000 | Normal Closure | Processing complete or client disconnected normally |
| 1001 | Going Away | Server shutting down or client navigating away |
| 1008 | Policy Violation | Permanent error (invalid video, unsupported platform) |
| 1011 | Server Error | Unexpected server error during processing |
| 4000 | Missing Authentication | No JWT token provided |
| 4001 | Unauthorized | Invalid or expired JWT token |
| 4004 | Not Found | Video ID does not exist or not owned by user |
| 4429 | Rate Limit Exceeded | Too many connections or requests |

---

## Example Flow

### Successful Processing

```
Client → Server: WebSocket connection to /ws/{video_id}?token={jwt}

Server → Client:
{
  "type": "connected",
  "video_id": "123...",
  "current_status": "extracting",
  "timestamp": 1716336000000
}

Server → Client:
{
  "type": "progress",
  "stage": "extracting",
  "percent": 30,
  "message": "Downloading video...",
  "timestamp": 1716336010000
}

Server → Client:
{
  "type": "stage_complete",
  "stage": "extracting",
  "next_stage": "transcribing",
  "timestamp": 1716336045000
}

Server → Client:
{
  "type": "progress",
  "stage": "transcribing",
  "percent": 45,
  "message": "Transcribing audio (3:45 of 8:20 processed)",
  "timestamp": 1716336090000
}

Server → Client:
{
  "type": "complete",
  "video_id": "123...",
  "transcription_id": "987...",
  "summary_id": "456...",
  "timestamp": 1716336245000
}

Server → Client: Close connection (code 1000)
```

### Error with Retry

```
Server → Client:
{
  "type": "error",
  "error_code": "TRN-001",
  "message": "Transcription service unavailable",
  "retry_attempt": 1,
  "max_retries": 3,
  "timestamp": 1716336100000
}

[10 seconds later - automatic retry]

Server → Client:
{
  "type": "progress",
  "stage": "transcribing",
  "percent": 20,
  "message": "Retrying transcription...",
  "timestamp": 1716336110000
}

[Processing continues normally]
```

---

## Security Considerations

1. **Authentication**: All connections require valid JWT token
2. **Authorization**: Users can only connect to their own videos
3. **Rate Limiting**: Max 5 concurrent WebSocket connections per user
4. **Timeout**: Idle connections closed after 10 minutes
5. **Message Size**: Max message size 64KB (server enforced)
6. **Origin Validation**: CORS-like origin checking for browser connections

---

## Error Handling Best Practices

**Client Implementation**:
1. Implement automatic reconnection with exponential backoff
2. Handle all close codes gracefully
3. Store partial progress locally for recovery
4. Fall back to REST API polling if WebSocket fails repeatedly
5. Display user-friendly error messages from server events

**Example Reconnection Logic**:
```typescript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connect() {
  const ws = new WebSocket(`ws://api/v1/ws/${videoId}?token=${token}`);
  
  ws.onclose = (event) => {
    if (event.code === 1000 || event.code === 1008) {
      // Normal closure or permanent error - don't reconnect
      return;
    }
    
    if (reconnectAttempts < maxReconnectAttempts) {
      const delay = Math.pow(2, reconnectAttempts) * 1000; // Exponential backoff
      setTimeout(connect, delay);
      reconnectAttempts++;
    } else {
      // Fall back to REST API polling
      startPolling();
    }
  };
}
```

---

## Testing

**Manual Testing**:
Use `wscat` for command-line testing:
```bash
wscat -c "ws://localhost:8000/api/v1/ws/{video_id}?token={jwt}"
```

**Automated Testing**:
Use `pytest-asyncio` with `websockets` library:
```python
async def test_websocket_progress_updates():
    async with websockets.connect(f"ws://localhost:8000/api/v1/ws/{video_id}") as ws:
        await ws.send(json.dumps({"type": "auth", "token": jwt_token}))
        msg = await ws.recv()
        assert json.loads(msg)["type"] == "connected"
```

---

## Summary

WebSocket contract provides real-time, bidirectional communication for video processing status updates. Structured event types with clear schemas enable robust client implementations. Comprehensive error handling and reconnection strategies ensure reliable operation even under adverse network conditions.