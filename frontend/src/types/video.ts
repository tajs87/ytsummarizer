/**
 * Type definitions for video entities and operations.
 */

export type VideoStatus =  | 'PENDING'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED';

export interface Video {
  id: number;
  url: string;
  title: string | null;
  duration_seconds: number | null;
  status: VideoStatus;
  error_message: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface VideoSubmitRequest {
  url: string;
}

export interface VideoSubmitResponse {
  id: number;
  url: string;
  status: VideoStatus;
  message: string;
}

export interface VideoListResponse {
  videos: Video[];
  total: number;
}

export interface VideoDetailResponse extends Video {
  has_transcription: boolean;
}
