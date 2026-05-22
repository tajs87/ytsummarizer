/**
 * Type definitions for video entities and operations.
 */

export type VideoStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export type Video = {
  id: number;
  url: string;
  title: string | null;
  duration_seconds: number | null;
  status: VideoStatus;
  error_message: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
};

export type VideoSubmitRequest = {
  url: string;
};

export type VideoSubmitResponse = {
  id: number;
  url: string;
  status: VideoStatus;
  message: string;
};

export type VideoListResponse = {
  videos: Video[];
  total: number;
};

export type VideoDetailResponse = {
  has_transcription: boolean;
} & Video;
