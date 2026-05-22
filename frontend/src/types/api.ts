/**
 * TypeScript types for API contracts.
 * Matches backend Pydantic schemas.
 */

export type VideoPlatform = 'YOUTUBE' | 'VIMEO' | 'DIRECT';

export type VideoStatus = 'PENDING' | 'EXTRACTING' | 'TRANSCRIBING' | 'COMPLETED' | 'FAILED';

export type Video = {
  id: number;
  url: string;
  platform: VideoPlatform;
  title: string | null;
  duration_seconds: number | null;
  status: VideoStatus;
  error_message: string | null;
  task_id: string | null;
  created_at: string;
  completed_at: string | null;
  has_transcription: boolean;
};

export type VideoSubmitRequest = {
  url: string;
};

export type VideoListResponse = {
  videos: Video[];
  total: number;
  page: number;
  page_size: number;
  is_guest_context?: boolean;
  history_scope?: 'account' | 'session';
};

export type TranscriptionSegment = {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker?: string;
};

export type Transcription = {
  id: number;
  video_id: number;
  full_text: string;
  segments: TranscriptionSegment[];
  language: string;
  word_count: number;
  processing_time_seconds: number | null;
  created_at: string;
};

export type TranscriptionSearchRequest = {
  query: string;
};

export type TranscriptionSearchResult = {
  segment: TranscriptionSegment;
  match_count: number;
};

export type TranscriptionSearchResponse = {
  query: string;
  total_matches: number;
  results: TranscriptionSearchResult[];
};

export type ProgressUpdate = {
  progress: number;
  message: string;
  status: 'processing' | 'completed' | 'failed';
};

export type AuthToken = {
  access_token: string;
  token_type: string;
  migrated_items?: number;
};

export type User = {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
};

export type UserRegisterRequest = {
  email: string;
  password: string;
};

export type UserLoginRequest = {
  email: string;
  password: string;
};

export type ErrorResponse = {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
};
