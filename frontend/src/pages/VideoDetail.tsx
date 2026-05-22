/**
 * VideoDetail page.
 * Shows video details and transcription with full functionality.
 */
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useVideo } from '@/services/videos';
import { useTranscription } from '@/services/transcriptions';
import { TranscriptionView } from '@/components/TranscriptionView';
import { ProgressTracker } from '@/components/ProgressTracker';
import { SummaryPanel } from '@/components/SummaryPanel';

export function VideoDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const videoId = id ? parseInt(id, 10) : null;

  const { data: video, isLoading: videoLoading, error: videoError } = useVideo(videoId);
  const { data: transcription, isLoading: transcriptionLoading } = useTranscription(videoId);

  if (videoLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (videoError || !video) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <h2 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
              Video Not Found
            </h2>
            <p className="text-sm text-red-700 dark:text-red-300 mb-4">
              The requested video could not be found.
            </p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Go Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400">
            Home
          </Link>
          <span>/</span>
          <Link to="/history" className="hover:text-blue-600 dark:hover:text-blue-400">
            History
          </Link>
          <span>/</span>
          <span className="text-gray-900 dark:text-white">
            {video.title || 'Video'}
          </span>
        </nav>

        {/* Video info card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {video.title || 'Untitled Video'}
              </h1>
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline break-all"
              >
                {video.url}
              </a>
            </div>
            <div className="flex-shrink-0 ml-4">
              <span
                className={`px-3 py-1 text-sm font-medium rounded-full ${
                  video.status === 'COMPLETED'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                    : video.status === 'FAILED'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
                }`}
              >
                {video.status}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
            <div>
              <span className="font-medium">Platform:</span> {video.platform}
            </div>
            {video.duration_seconds && (
              <div>
                <span className="font-medium">Duration:</span>{' '}
                {Math.floor(video.duration_seconds / 60)} min {Math.floor(video.duration_seconds % 60)} sec
              </div>
            )}
            <div>
              <span className="font-medium">Submitted:</span>{' '}
              {new Date(video.created_at).toLocaleString()}
            </div>
            {video.completed_at && (
              <div>
                <span className="font-medium">Completed:</span>{' '}
                {new Date(video.completed_at).toLocaleString()}
              </div>
            )}
          </div>

          {video.error_message && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">
                <span className="font-medium">Error:</span> {video.error_message}
              </p>
            </div>
          )}
        </div>

        {/* Progress tracker for processing videos */}
        {video.task_id && video.status !== 'COMPLETED' && video.status !== 'FAILED' && (
          <ProgressTracker taskId={video.task_id} videoId={video.id} />
        )}

        {/* Transcription view */}
        {video.status === 'COMPLETED' && (
          <>
            {transcriptionLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
              </div>
            )}

            {transcription && (
              <>
                <SummaryPanel videoId={video.id} />
                <TranscriptionView
                  transcription={transcription}
                  videoTitle={video.title || 'Video'}
                />
              </>
            )}
          </>
        )}

        {/* Failed state */}
        {video.status === 'FAILED' && (
          <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
              Processing Failed
            </h3>
            <p className="text-sm text-red-700 dark:text-red-300 mb-4">
              {video.error_message || 'An error occurred during processing.'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Another Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
