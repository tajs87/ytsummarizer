/**
 * Hook for managing video processing state and operations.
 * Provides video submission, status tracking, and progress monitoring.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useVideoStore } from '../stores/videoStore';
import { apiClient } from '../services/api';
import { VideoSubmitRequest, VideoSubmitResponse } from '../types/video';

export function useVideoProcessing() {
  const queryClient = useQueryClient();
  const { addProcessingVideo, removeProcessingVideo, updateVideoStatus, updateVideoProgress } =
    useVideoStore();

  const submitVideo = useMutation({
    mutationFn: async (data: VideoSubmitRequest): Promise<VideoSubmitResponse> => {
      const response = await apiClient.post<VideoSubmitResponse>('/api/v1/videos', data);
      return response.data;
    },
    onSuccess: (data) => {
      // Add video to processing queue
      addProcessingVideo(data.id);

      // Invalidate videos list to refetch
      void queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
  });

  const updateProgress = (videoId: number, progress: number) => {
    updateVideoProgress(videoId, progress);
  };

  const updateStatus = (
    videoId: number,
    status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  ) => {
    updateVideoStatus(videoId, status);

    // Remove from processing queue if completed or failed
    if (status === 'COMPLETED' || status === 'FAILED') {
      removeProcessingVideo(videoId);
      // Invalidate queries to refetch updated video
      void queryClient.invalidateQueries({ queryKey: ['videos'] });
      void queryClient.invalidateQueries({ queryKey: ['video', videoId] });
    }
  };

  return {
    submitVideo,
    updateProgress,
    updateStatus,
    isSubmitting: submitVideo.isPending,
    error: submitVideo.error,
  };
}
