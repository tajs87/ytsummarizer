/**
 * Type definitions for transcription entities and operations.
 */

export type TranscriptionSegment = {
  id: number;
  start_time: number;
  end_time: number;
  text: string;
}

export type Transcription = {
  id: number;
  video_id: number;
  full_text: string;
  language: string | null;
  segments: TranscriptionSegment[];
  created_at: string;
  updated_at: string;
}

export type TranscriptionResponse = {
  transcription: Transcription;
}

export type TranscriptionSearchRequest = {
  query: string;
  max_results?: number;
}

export type TranscriptionSearchResult = {
  segment_id: number;
  text: string;
  start_time: number;
  end_time: number;
  match_score: number;
}

export type TranscriptionSearchResponse = {
  results: TranscriptionSearchResult[];
  total: number;
}

export type ExportFormat = 'txt' | 'json' | 'csv';
