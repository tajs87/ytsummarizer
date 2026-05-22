/**
 * Video API service hooks.
 * Uses TanStack Query for data fetching and caching.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type {
  Video,
  VideoListResponse,
  VideoSubmitRequest,
  VideoStatus,
} from '@/types/api';

const VIDEOS_KEY = 'videos';

/**
 * Submit a video URL for transcription.
 */
export function useSubmitVideo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: VideoSubmitRequest) => {
      const response = await apiClient.post<Video>('/api/v1/videos', request);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate videos list to refetch
      queryClient.invalidateQueries({ queryKey: [VIDEOS_KEY] });
    },
  });
}

/**
 * Fetch list of user's videos with pagination and filtering.
 */
export function useVideos(
  page = 1,
  pageSize = 20,
  statusFilter?: VideoStatus
) {
  return useQuery({
    queryKey: [VIDEOS_KEY, page, pageSize, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (statusFilter) {
        params.append('status_filter', statusFilter);
      }

      const response = await apiClient.get<VideoListResponse>(
        `/api/v1/videos?${params.toString()}`
      );
      return response.data;
    },
  });
}

/**
 * Fetch details for a specific video.
 */
export function useVideo(videoId: number | null) {
  return useQuery({
    queryKey: [VIDEOS_KEY, videoId],
    queryFn: async () => {
      if (!videoId) throw new Error('Video ID is required');
      const response = await apiClient.get<Video>(`/api/v1/videos/${videoId}`);
      return response.data;
    },
    enabled: !!videoId,
  });
}

/**
 * Delete a video and its transcription.
 */
export function useDeleteVideo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (videoId: number) => {
      await apiClient.delete(`/api/v1/videos/${videoId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_KEY] });
    },
  });
}
