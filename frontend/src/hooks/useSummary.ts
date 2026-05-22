/**
 * Hook for summary generation and retrieval.
 */

import { useGenerateSummary, useVideoSummaries } from '../services/summaries';
import { SummaryType } from '../types/summary';

export function useSummary(videoId: number) {
  const generateMutation = useGenerateSummary(videoId);
  const summariesQuery = useVideoSummaries(videoId);

  const generateSummary = async (summaryType: SummaryType = 'brief') => {
    return generateMutation.mutateAsync({ summary_type: summaryType });
  };

  return {
    summaries: summariesQuery.data?.summaries || [],
    total: summariesQuery.data?.total || 0,
    isLoading: summariesQuery.isLoading,
    error: summariesQuery.error,
    refetch: summariesQuery.refetch,
    generateSummary,
    isGenerating: generateMutation.isPending,
    generateError: generateMutation.error,
  };
}
