/**
 * Type definitions for highlight entities.
 */

export type Highlight = {
  id: number;
  summary_id: number;
  text: string;
  start_time: number;
  end_time: number;
  importance_score: number | null;
  created_at: string;
}

export type HighlightListResponse = {
  highlights: Highlight[];
  total: number;
}
