/**
 * VideoList component.
 * Displays user's video history with filtering and status.
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useVideos, useDeleteVideo } from '@/services/videos';
import type { VideoStatus } from '@/types/api';

export function VideoList() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<VideoStatus | undefined>();
  const { data, isLoading, error } = useVideos(page, 20, statusFilter);
  const deleteVideo = useDeleteVideo();
  const isGuestContext = data?.is_guest_context ?? false;

  const handleDelete = async (videoId: number, videoTitle: string | null) => {
    if (
      !confirm(
        `Are you sure you want to delete "${videoTitle ?? 'this video'}"?`
      )
    ) {
      return;
    }

    try {
      await deleteVideo.mutateAsync(videoId);
    } catch (error) {
      console.error('Failed to delete video:', error);
      alert('Failed to delete video');
    }
  };

  const getStatusBadge = (status: VideoStatus) => {
    const styles = {
      PENDING: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      EXTRACTING:
        'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      TRANSCRIBING:
        'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300',
      COMPLETED:
        'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      FAILED: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status]}`}
      >
        {status}
      </span>
    );
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'YOUTUBE':
        return '▶️';
      case 'VIMEO':
        return '🎬';
      default:
        return '🎥';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    const errorMessage =
      error instanceof Error ? error.message : 'Failed to load videos. Please try again.';

    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-sm text-red-800 dark:text-red-200">
          {errorMessage}
        </p>
      </div>
    );
  }

  if (!data || data.videos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">
          {isGuestContext
            ? 'No guest-session videos found. Submit a video to start processing in this session.'
            : 'No videos found. Start by submitting a video URL!'}
        </p>
        {isGuestContext && (
          <p className="mt-2 text-sm text-amber-700 dark:text-amber-300">
            Guest history is temporary and clears when your browser session ends.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {isGuestContext && (
        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg text-sm text-amber-800 dark:text-amber-200">
          You are viewing guest session history. Sign in to migrate these items to your account.
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Filter by status:
        </label>
        <select
          value={statusFilter ?? ''}
          onChange={(e) =>
            { setStatusFilter(
              e.target.value ? (e.target.value as VideoStatus) : undefined
            ); }
          }
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All</option>
          <option value="PENDING">Pending</option>
          <option value="EXTRACTING">Extracting</option>
          <option value="TRANSCRIBING">Transcribing</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
        </select>
      </div>

      {/* Video list */}
      <div className="space-y-4">
        {data.videos.map((video) => (
          <div
            key={video.id}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 
                     p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{getPlatformIcon(video.platform)}</span>
                  <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                    {video.platform}
                  </span>
                  <Link
                    to={`/video/${video.id}`}
                    className="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 truncate"
                  >
                    {video.title ?? 'Untitled Video'}
                  </Link>
                  {getStatusBadge(video.status)}
                </div>

                <p className="text-sm text-gray-500 dark:text-gray-400 truncate mb-2">
                  {video.url}
                </p>

                <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                  <span>
                    Submitted:{' '}
                    {new Date(video.created_at).toLocaleDateString()}
                  </span>
                  {video.duration_seconds && (
                    <span>
                      Duration:{' '}
                      {Math.floor(video.duration_seconds / 60)} min
                    </span>
                  )}
                  {video.has_transcription && (
                    <span className="text-green-600 dark:text-green-400">
                      ✓ Transcription available
                    </span>
                  )}
                </div>

                {video.error_message && (
                  <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                    Error: {video.error_message}
                  </p>
                )}
              </div>

              <div className="flex-shrink-0 flex gap-2">
                {video.status === 'COMPLETED' && (
                  <Link
                    to={`/video/${video.id}`}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    View
                  </Link>
                )}
                <button
                  onClick={() => handleDelete(video.id, video.title)}
                  disabled={deleteVideo.isPending}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg 
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {data.total > data.page_size && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => { setPage((p) => Math.max(1, p - 1)); }}
            disabled={page === 1}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          <span className="text-sm text-gray-500 dark:text-gray-400">
            Page {page} of {Math.ceil(data.total / data.page_size)}
          </span>

          <button
            onClick={() => { setPage((p) => p + 1); }}
            disabled={page >= Math.ceil(data.total / data.page_size)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                     text-gray-700 dark:text-gray-200 rounded-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
