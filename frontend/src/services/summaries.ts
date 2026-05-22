/**
 * API service hooks for summary operations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api';
import { Summary, SummaryListResponse, SummaryRequest } from '../types/summary';

export function useGenerateSummary(videoId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SummaryRequest): Promise<Summary> => {
      const response = await apiClient.post<Summary>(`/api/v1/videos/${videoId}/summaries`, data);
      return response.data;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['summaries', videoId] });
    },
  });
}

export function useVideoSummaries(videoId: number) {
  return useQuery({
    queryKey: ['summaries', videoId],
    queryFn: async (): Promise<SummaryListResponse> => {
      const response = await apiClient.get<SummaryListResponse>(`/api/v1/videos/${videoId}/summaries`);
      return response.data;
    },
    enabled: !!videoId,
  });
}

export function useSummary(summaryId: number) {
  return useQuery({
    queryKey: ['summary', summaryId],
    queryFn: async (): Promise<Summary> => {
      const response = await apiClient.get<Summary>(`/api/v1/videos/summaries/${summaryId}`);
      return response.data;
    },
    enabled: !!summaryId,
  });
}
