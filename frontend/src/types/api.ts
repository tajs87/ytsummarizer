/**
 * TypeScript types for API contracts.
 * Matches backend Pydantic schemas.
 */

export type VideoPlatform = 'YOUTUBE' | 'VIMEO' | 'DIRECT';

export type VideoStatus = 
  | 'PENDING' 
  | 'EXTRACTING' 
  | 'TRANSCRIBING' 
  | 'COMPLETED' 
  | 'FAILED';

export interface Video {
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
}

export interface VideoSubmitRequest {
  url: string;
}

export interface VideoListResponse {
  videos: Video[];
  total: number;
  page: number;
  page_size: number;
}

export interface TranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker?: string;
}

export interface Transcription {
  id: number;
  video_id: number;
  full_text: string;
  segments: TranscriptionSegment[];
  language: string;
  word_count: number;
  processing_time_seconds: number | null;
  created_at: string;
}

export interface TranscriptionSearchRequest {
  query: string;
}

export interface TranscriptionSearchResult {
  segment: TranscriptionSegment;
  match_count: number;
}

export interface TranscriptionSearchResponse {
  query: string;
  total_matches: number;
  results: TranscriptionSearchResult[];
}

export interface ProgressUpdate {
  progress: number;
  message: string;
  status: 'processing' | 'completed' | 'failed';
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface UserRegisterRequest {
  email: string;
  password: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}
