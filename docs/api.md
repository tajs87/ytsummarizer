# API Documentation

## Base URL

- Development: `http://localhost:8000/api/v1`

## Authentication

Most endpoints require Bearer JWT authentication:

```http
Authorization: Bearer <access_token>
```

## Auth Endpoints

### POST /auth/register
Create a new user account.

### POST /auth/login
Login with email/password and receive JWT token.

### GET /auth/me
Get current authenticated user.

## Video Endpoints

### POST /videos
Submit a video URL for transcription processing.

Request:
```json
{
  "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"
}
```

### GET /videos
List user's submitted videos.

### GET /videos/{id}
Get details for a specific video.

### DELETE /videos/{id}
Delete a video and related data.

## Transcription Endpoints

### GET /videos/{id}/transcription
Get full transcription for a video.

### POST /videos/{id}/transcription/search
Search within transcription text.

## Summary Endpoints

### POST /videos/{id}/summaries
Generate AI summary for a transcribed video.

Request:
```json
{
  "summary_type": "brief"
}
```

Allowed summary types:
- `brief`
- `detailed`
- `bullet_points`

### GET /videos/{id}/summaries
List summaries for a video.

### GET /videos/summaries/{summary_id}
Get a specific summary by ID.

## Share Endpoints

### POST /videos/{id}/share
Create a shareable timestamp link.

Request:
```json
{
  "start_time": 30.5,
  "end_time": 45.0,
  "title": "Key moment",
  "expires_in_hours": 24
}
```

### GET /share/{token}
Public endpoint to access shared content (no auth required).

## Health Endpoint

### GET /health
Service health check.
