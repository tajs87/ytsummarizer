/**
 * Type definitions for shareable links and sharing operations.
 */

export type ShareLinkRequest = {
  start_time: number;
  end_time?: number;
  title?: string;
  expires_in_hours?: number;
};

export type ShareLinkResponse = {
  id: number;
  video_id: number;
  token: string;
  share_url: string;
  start_time: number;
  end_time: number | null;
  title: string | null;
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
};

export type SharedContentResponse = {
  video_id: number;
  video_title: string | null;
  transcription_text: string;
  start_time: number;
  end_time: number | null;
  title: string | null;
};
