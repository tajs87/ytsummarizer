/**
 * Summary panel for generating and viewing AI summaries.
 */

import { useState } from 'react';
import { useSummary } from '@/hooks/useSummary';
import { SummaryType } from '@/types/summary';
import { SummaryTypeSelector } from '@/components/SummaryTypeSelector';
import { HighlightsList } from '@/components/HighlightsList';

type SummaryPanelProps = {
  videoId: number;
  onTimestampClick?: (timeInSeconds: number) => void;
};

export function SummaryPanel({ videoId, onTimestampClick }: SummaryPanelProps) {
  const [selectedType, setSelectedType] = useState<SummaryType>('brief');
  const [isWaitingForSummary, setIsWaitingForSummary] = useState(false);
  const { summaries, isLoading, isGenerating, generateSummary, generateError } =
    useSummary(videoId);

  const selectedSummary =
    [...summaries]
      .filter((summary) => summary.summary_type === selectedType)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0] ??
    [...summaries].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];

  const handleGenerate = async () => {
    setIsWaitingForSummary(true);
    try {
      await generateSummary(selectedType);
    } catch (error) {
      // Keep local handling minimal; query state renders the error.
      console.error('Summary generation failed', error);
    } finally {
      setIsWaitingForSummary(false);
    }
  };

  const isBusy = isGenerating || isWaitingForSummary;

  return (
    <section className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">AI Summary</h2>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={isBusy}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isBusy ? 'Generating...' : 'Generate Summary'}
        </button>
      </div>

      <SummaryTypeSelector value={selectedType} onChange={setSelectedType} disabled={isBusy} />

      {isBusy && (
        <p className="text-sm text-blue-600 dark:text-blue-400">
          Generating summary, this may take a few seconds...
        </p>
      )}

      {generateError && (
        <p className="text-sm text-red-600 dark:text-red-400">
          Failed to generate summary. Please try again.
        </p>
      )}

      {isLoading ? (
        <div className="py-6 text-sm text-gray-500 dark:text-gray-400">Loading summaries...</div>
      ) : selectedSummary ? (
        <>
          <div className="p-4 bg-gray-50 dark:bg-gray-900/40 rounded-lg border border-gray-200 dark:border-gray-700">
            <p className="whitespace-pre-wrap text-gray-900 dark:text-gray-100">
              {selectedSummary.content}
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="font-medium text-gray-900 dark:text-white">Highlights</h3>
            <HighlightsList
              videoId={videoId}
              highlights={selectedSummary.highlights}
              {...(onTimestampClick ? { onTimestampClick } : {})}
            />
          </div>
        </>
      ) : (
        <div className="py-6 text-sm text-gray-500 dark:text-gray-400">
          No summaries yet. Select a type and generate one.
        </div>
      )}
    </section>
  );
}
