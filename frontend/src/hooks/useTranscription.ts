/**
 * Hook for managing transcription operations.
 * Provides transcription fetching, searching, and exporting.
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import {
  Transcription,
  TranscriptionSearchRequest,
  TranscriptionSearchResponse,
  ExportFormat,
} from '../types/transcription';

export function useTranscription(videoId: number) {
  // Fetch transcription for a video
  const transcriptionQuery = useQuery({
    queryKey: ['transcription', videoId],
    queryFn: async () => {
      const response = await apiClient.get<{ transcription: Transcription }>(
        `/api/v1/videos/${videoId}/transcription`
      );
      return response.data.transcription;
    },
    enabled: !!videoId,
    retry: 1,
  });

  // Search within transcription
  const searchMutation = useMutation({
    mutationFn: async (data: TranscriptionSearchRequest): Promise<TranscriptionSearchResponse> => {
      const response = await apiClient.post<TranscriptionSearchResponse>(
        `/api/v1/videos/${videoId}/transcription/search`,
        data
      );
      return response.data;
    },
  });

  // Export transcription
  const exportTranscription = async (format: ExportFormat) => {
    if (!transcriptionQuery.data) return;

    const transcription = transcriptionQuery.data;
    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'txt':
        content = transcription.full_text;
        filename = `transcription_${videoId}.txt`;
        mimeType = 'text/plain';
        break;
      case 'json':
        content = JSON.stringify(transcription, null, 2);
        filename = `transcription_${videoId}.json`;
        mimeType = 'application/json';
        break;
      case 'csv':
        const csvRows = [
          ['Start Time', 'End Time', 'Text'],
          ...transcription.segments.map((seg) => [
            seg.start_time.toFixed(2),
            seg.end_time.toFixed(2),
            `"${seg.text.replace(/"/g, '""')}"`,
          ]),
        ];
        content = csvRows.map((row) => row.join(',')).join('\n');
        filename = `transcription_${videoId}.csv`;
        mimeType = 'text/csv';
        break;
    }

    // Create and download file
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return {
    transcription: transcriptionQuery.data,
    isLoading: transcriptionQuery.isLoading,
    error: transcriptionQuery.error,
    refetch: transcriptionQuery.refetch,
    search: searchMutation.mutate,
    searchResults: searchMutation.data,
    isSearching: searchMutation.isPending,
    exportTranscription,
  };
}
