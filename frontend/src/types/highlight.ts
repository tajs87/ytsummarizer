/**
 * Type definitions for highlight entities.
 */

export interface Highlight {
  id: number;
  summary_id: number;
  text: string;
  start_time: number;
  end_time: number;
  importance_score: number | null;
  created_at: string;
}

export interface HighlightListResponse {
  highlights: Highlight[];
  total: number;
}
