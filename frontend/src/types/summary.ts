/**
 * Type definitions for summary entities.
 */

import { Highlight } from './highlight';

export type SummaryType = 'brief' | 'detailed' | 'bullet_points';

export interface Summary {
  id: number;
  video_id: number;
  summary_type: SummaryType;
  content: string;
  highlights: Highlight[];
  created_at: string;
  updated_at: string;
}

export interface SummaryRequest {
  summary_type: SummaryType;
}

export interface SummaryListResponse {
  summaries: Summary[];
  total: number;
}
