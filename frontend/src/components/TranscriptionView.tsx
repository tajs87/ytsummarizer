/**
 * TranscriptionView component.
 * Displays transcription with view/copy/export/search functionality.
 */
import { useState } from 'react';
import type { Transcription } from '@/types/api';
import { useSearchTranscription, exportTranscription } from '@/services/transcriptions';
import { ShareDialog } from '@/components/ShareDialog';

type TranscriptionViewProps = {
  transcription: Transcription;
  videoTitle?: string;
};

export function TranscriptionView({ transcription, videoTitle }: TranscriptionViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'full' | 'segments'>('segments');
  const searchMutation = useSearchTranscription(transcription.video_id);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(transcription.full_text);
      alert('Transcription copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy:', error);
      alert('Failed to copy to clipboard');
    }
  };

  const handleExportTXT = async () => {
    try {
      const text = await exportTranscription(transcription.video_id);
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transcription-${transcription.video_id}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export:', error);
      alert('Failed to export transcription');
    }
  };

  const handleExportJSON = () => {
    const json = JSON.stringify(transcription, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${transcription.video_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    const headers = ['ID', 'Start', 'End', 'Text'];
    const rows = transcription.segments.map((seg) => [
      seg.id,
      seg.start.toFixed(2),
      seg.end.toFixed(2),
      `"${seg.text.replace(/"/g, '""')}"`, // Escape quotes
    ]);

    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${transcription.video_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      await searchMutation.mutateAsync({ query: searchQuery.trim() });
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const formatTimestamp = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const highlightText = (text: string, query: string): JSX.Element => {
    if (!query) return <>{text}</>;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return (
      <>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 dark:bg-yellow-800">
              {part}
            </mark>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </>
    );
  };

  const displaySegments = searchMutation.data
    ? searchMutation.data.results.map(
        (r: { segment: { id: number; start: number; end: number; text: string } }) => r.segment
      )
    : transcription.segments;

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {videoTitle ?? 'Transcription'}
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {transcription.word_count.toLocaleString()} words •{' '}
            {transcription.language.toUpperCase()} • {transcription.segments.length} segments
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleCopy}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
            title="Copy to clipboard"
          >
            📋 Copy
          </button>
          <button
            onClick={handleExportTXT}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
          >
            📄 TXT
          </button>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
          >
            📊 CSV
          </button>
          <button
            onClick={handleExportJSON}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
          >
            🔧 JSON
          </button>
        </div>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
          }}
          placeholder="Search within transcription..."
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   dark:bg-gray-800 dark:text-white"
        />
        <button
          type="submit"
          disabled={searchMutation.isPending}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg
                   disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {searchMutation.isPending ? 'Searching...' : 'Search'}
        </button>
        {searchMutation.data && (
          <button
            type="button"
            onClick={() => {
              setSearchQuery('');
              searchMutation.reset();
            }}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg transition-colors"
          >
            Clear
          </button>
        )}
      </form>

      {searchMutation.data && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            Found {searchMutation.data.total_matches} result
            {searchMutation.data.total_matches !== 1 ? 's' : ''} for &ldquo;
            {searchMutation.data.query}&rdquo;
          </p>
        </div>
      )}

      {/* View mode toggle */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => {
            setViewMode('segments');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            viewMode === 'segments'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
          }`}
        >
          Segments
        </button>
        <button
          onClick={() => {
            setViewMode('full');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            viewMode === 'full'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
          }`}
        >
          Full Text
        </button>
      </div>

      {/* Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        {viewMode === 'full' ? (
          <div className="prose dark:prose-invert max-w-none">
            <p className="whitespace-pre-wrap text-gray-900 dark:text-gray-100">
              {highlightText(transcription.full_text, searchQuery)}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {displaySegments.map(
              (segment: { id: number; start: number; end?: number; text: string }) => (
                <div
                  key={segment.id}
                  className="flex gap-4 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors"
                >
                  <div className="flex-shrink-0 text-sm font-mono text-gray-500 dark:text-gray-400">
                    {formatTimestamp(segment.start)}
                  </div>
                  <p className="flex-1 text-gray-900 dark:text-gray-100">
                    {highlightText(segment.text, searchQuery)}
                  </p>
                  <div className="flex-shrink-0">
                    <ShareDialog
                      videoId={transcription.video_id}
                      startTime={segment.start}
                      {...(typeof segment.end === 'number' ? { endTime: segment.end } : {})}
                    />
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}
