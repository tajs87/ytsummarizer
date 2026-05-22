/**
 * Type definitions for transcription entities and operations.
 */

export interface TranscriptionSegment {
  id: number;
  start_time: number;
  end_time: number;
  text: string;
}

export interface Transcription {
  id: number;
  video_id: number;
  full_text: string;
  language: string | null;
  segments: TranscriptionSegment[];
  created_at: string;
  updated_at: string;
}

export interface TranscriptionResponse {
  transcription: Transcription;
}

export interface TranscriptionSearchRequest {
  query: string;
  max_results?: number;
}

export interface TranscriptionSearchResult {
  segment_id: number;
  text: string;
  start_time: number;
  end_time: number;
  match_score: number;
}

export interface TranscriptionSearchResponse {
  results: TranscriptionSearchResult[];
  total: number;
}

export type ExportFormat = 'txt' | 'json' | 'csv';
