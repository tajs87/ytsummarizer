/**
 * Render summary highlights with timestamp navigation and sharing.
 */

import { Highlight } from '@/types/highlight';
import { formatTimestamp } from '@/utils/formatTimestamp';
import { ShareDialog } from '@/components/ShareDialog';
import { TimestampLink } from '@/components/TimestampLink';

type HighlightsListProps = {
  videoId: number;
  highlights: Highlight[];
  onTimestampClick?: (timeInSeconds: number) => void;
};

export function HighlightsList({
  videoId,
  highlights,
  onTimestampClick,
}: HighlightsListProps) {
  if (!highlights.length) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400">No highlights available yet.</p>
    );
  }

  return (
    <div className="space-y-3">
      {highlights.map((highlight) => (
        <div
          key={highlight.id}
          className="p-3 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <p className="text-sm text-gray-900 dark:text-gray-100">{highlight.text}</p>
              <div className="mt-2 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <TimestampLink
                  timeInSeconds={highlight.start_time}
                  {...(onTimestampClick ? { onClick: onTimestampClick } : {})}
                />
                <span>-</span>
                <TimestampLink
                  timeInSeconds={highlight.end_time}
                  {...(onTimestampClick ? { onClick: onTimestampClick } : {})}
                />
                <span>
                  ({formatTimestamp(highlight.end_time - highlight.start_time)})
                </span>
                {typeof highlight.importance_score === 'number' && (
                  <span className="ml-2 px-2 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                    Score: {Math.round(highlight.importance_score * 100)}%
                  </span>
                )}
              </div>
            </div>

            <ShareDialog
              videoId={videoId}
              startTime={highlight.start_time}
              endTime={highlight.end_time}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
