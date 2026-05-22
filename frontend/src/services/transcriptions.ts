/**
 * Transcription API service hooks.
 * Uses TanStack Query for data fetching and caching.
 */
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from './api';
import type {
  Transcription,
  TranscriptionSearchRequest,
  TranscriptionSearchResponse,
} from '@/types/api';

const TRANSCRIPTIONS_KEY = 'transcriptions';

/**
 * Fetch transcription for a video.
 */
export function useTranscription(videoId: number | null) {
  return useQuery({
    queryKey: [TRANSCRIPTIONS_KEY, videoId],
    queryFn: async () => {
      if (!videoId) throw new Error('Video ID is required');
      const response = await apiClient.get<Transcription>(
        `/api/v1/videos/${videoId}/transcription`
      );
      return response.data;
    },
    enabled: !!videoId,
    retry: false, // Don't retry if transcription not ready
  });
}

/**
 * Search within a transcription.
 */
export function useSearchTranscription(videoId: number) {
  return useMutation({
    mutationFn: async (request: TranscriptionSearchRequest) => {
      const response = await apiClient.post<TranscriptionSearchResponse>(
        `/api/v1/videos/${videoId}/transcription/search`,
        request
      );
      return response.data;
    },
  });
}

/**
 * Export transcription as plain text.
 */
export async function exportTranscription(videoId: number): Promise<string> {
  const response = await fetch(
    `${import.meta.env['VITE_API_URL']}/api/v1/videos/${videoId}/transcription/export`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to export transcription');
  }

  return response.text();
}
