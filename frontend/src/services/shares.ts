/**
 * API service for share link operations.
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from './api';
import { ShareLinkRequest, ShareLinkResponse, SharedContentResponse } from '../types/share';

export function useCreateShareLink(videoId: number) {
  return useMutation({
    mutationFn: async (data: ShareLinkRequest): Promise<ShareLinkResponse> => {
      const response = await apiClient.post<ShareLinkResponse>(
        `/api/v1/videos/${videoId}/share`,
        data
      );
      return response.data;
    },
  });
}

export function useSharedContent(token: string) {
  return useQuery({
    queryKey: ['shared-content', token],
    queryFn: async (): Promise<SharedContentResponse> => {
      const response = await apiClient.get<SharedContentResponse>(`/api/v1/share/${token}`);
      return response.data;
    },
    enabled: !!token,
    retry: false,
  });
}
