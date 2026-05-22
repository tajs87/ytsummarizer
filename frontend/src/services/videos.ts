/**
 * Video API service hooks.
 * Uses TanStack Query for data fetching and caching.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import type {
  Video,
  VideoListResponse,
  VideoPlatform,
  VideoSubmitRequest,
  VideoStatus,
} from '@/types/api';

const VIDEOS_KEY = 'videos';

type ApiVideo = Omit<Video, 'status' | 'platform'> & {
  status: string;
  platform: string;
};

function normalizeVideo(video: ApiVideo): Video {
  return {
    ...video,
    status: video.status.toUpperCase() as VideoStatus,
    platform: video.platform.toUpperCase() as VideoPlatform,
  };
}

function toApiStatus(status: VideoStatus): string {
  return status.toLowerCase();
}

/**
 * Submit a video URL for transcription.
 */
export function useSubmitVideo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: VideoSubmitRequest) => {
      const response = await apiClient.post<ApiVideo>('/api/v1/videos', request);
      return normalizeVideo(response.data);
    },
    onSuccess: () => {
      // Invalidate videos list to refetch
      void queryClient.invalidateQueries({ queryKey: [VIDEOS_KEY] });
    },
  });
}

/**
 * Fetch list of user's videos with pagination and filtering.
 */
export function useVideos(page = 1, pageSize = 20, statusFilter?: VideoStatus) {
  return useQuery({
    queryKey: [VIDEOS_KEY, page, pageSize, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });

      if (statusFilter) {
        params.append('status_filter', toApiStatus(statusFilter));
      }

      const response = await apiClient.get<{
        videos: ApiVideo[];
        total: number;
        page: number;
        page_size: number;
        is_guest_context?: boolean;
        history_scope?: 'account' | 'session';
      }>(`/api/v1/videos?${params.toString()}`);

      const normalized: VideoListResponse = {
        ...response.data,
        videos: response.data.videos.map(normalizeVideo),
        is_guest_context: response.data.is_guest_context ?? false,
        history_scope: response.data.history_scope ?? 'account',
      };

      return normalized;
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
      const response = await apiClient.get<ApiVideo>(`/api/v1/videos/${videoId}`);
      return normalizeVideo(response.data);
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
      void queryClient.invalidateQueries({ queryKey: [VIDEOS_KEY] });
    },
  });
}
