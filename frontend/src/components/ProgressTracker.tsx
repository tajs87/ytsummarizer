/**
 * ProgressTracker component.
 * Shows real-time progress updates via WebSocket.
 */
import { useProgressWebSocket } from '@/hooks/useProgressWebSocket';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

type ProgressTrackerProps = {
  taskId: string | null;
  videoId?: number;
};

export function ProgressTracker({ taskId, videoId }: ProgressTrackerProps) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const handleViewClick = () => {
    if (!videoId) return;

    try {
      navigate(`/video/${videoId}`);
    } catch {
      window.location.href = `/video/${videoId}`;
    }
  };

  const { progress, isConnected } = useProgressWebSocket({
    taskId,
    onComplete: () => {
      // Invalidate video and transcription queries when complete
      if (videoId) {
        void queryClient.invalidateQueries({ queryKey: ['videos', videoId] });
        void queryClient.invalidateQueries({ queryKey: ['transcriptions', videoId] });
      }
      void queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
  });

  if (!taskId) {
    return null;
  }

  const progressPercent = progress?.progress ?? 0;
  const message = progress?.message ?? 'Initializing...';
  const status = progress?.status ?? 'processing';

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-600';
      case 'failed':
        return 'bg-red-600';
      default:
        return 'bg-blue-600';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return (
          <svg
            className="w-5 h-5 text-green-600"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'failed':
        return (
          <svg
            className="w-5 h-5 text-red-600"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return (
          <svg
            className="animate-spin w-5 h-5 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        );
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Processing Video
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-gray-400'
            }`}
          />
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-300">{message}</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {progressPercent}%
          </span>
        </div>

        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full ${getStatusColor()} transition-all duration-300 ease-out`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {status === 'failed' && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-200">
            Processing failed. Please try again or contact support.
          </p>
        </div>
      )}

      {status === 'completed' && (
        <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm text-green-800 dark:text-green-200 mb-3">
            Transcription complete! You can now view the results.
          </p>
          {videoId && (
            <button
              onClick={handleViewClick}
              className="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              View Transcription
            </button>
          )}
        </div>
      )}
    </div>
  );
}
