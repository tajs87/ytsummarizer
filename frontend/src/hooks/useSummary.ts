/**
 * Hook for summary generation and retrieval.
 */

import { useGenerateSummary, useVideoSummaries } from '../services/summaries';
import { SummaryType } from '../types/summary';

export function useSummary(videoId: number) {
  const generateMutation = useGenerateSummary(videoId);
  const summariesQuery = useVideoSummaries(videoId);

  const getLatestSummaryForType = (
    summaries: Array<{ summary_type: SummaryType; created_at: string; highlights: Array<unknown> }>,
    summaryType: SummaryType
  ) => {
    const matches = summaries
      .filter((summary) => summary.summary_type === summaryType)
      .sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    return matches[0];
  };

  const generateSummary = async (summaryType: SummaryType = 'brief') => {
    await generateMutation.mutateAsync({ summary_type: summaryType });

    // Summary generation runs asynchronously on Celery, so poll briefly
    // until the newly requested summary type and highlights are available.
    const maxAttempts = 8;
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const result = await summariesQuery.refetch();
      const summaries = result.data?.summaries ?? [];
      const matchingSummary = getLatestSummaryForType(summaries, summaryType);
      if (matchingSummary && matchingSummary.highlights.length > 0) {
        break;
      }
    }
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
