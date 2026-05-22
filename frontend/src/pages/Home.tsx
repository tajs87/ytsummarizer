/**
 * Home page.
 * Main landing page with video submission form.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VideoInput } from '@/components/VideoInput';
import { ProgressTracker } from '@/components/ProgressTracker';
import { useVideo } from '@/services/videos';

export function Home() {
  const [submittedVideoId, setSubmittedVideoId] = useState<number | null>(null);
  const navigate = useNavigate();
  const { data: video } = useVideo(submittedVideoId);

  const handleSubmitSuccess = (videoId: number) => {
    setSubmittedVideoId(videoId);
  };

  const handleViewTranscription = () => {
    if (submittedVideoId) {
      navigate(`/video/${submittedVideoId}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Video Transcription & Summarization
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Transform YouTube and Vimeo videos into searchable text transcripts
          </p>
        </div>

        {/* Video submission form */}
        <VideoInput onSubmitSuccess={handleSubmitSuccess} />

        {/* Progress tracker */}
        {video && video.task_id && video.status !== 'COMPLETED' && (
          <ProgressTracker taskId={video.task_id} videoId={video.id} />
        )}

        {/* Success message with view button */}
        {video && video.status === 'COMPLETED' && (
          <div className="max-w-2xl mx-auto p-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">
                  ✓ Transcription Complete
                </h3>
                <p className="mt-1 text-sm text-green-700 dark:text-green-300">
                  {video.title || 'Your video'} has been transcribed successfully
                </p>
              </div>
              <button
                onClick={handleViewTranscription}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
              >
                View Transcription
              </button>
            </div>
          </div>
        )}

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 pt-12">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-4">⚡</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Fast Processing
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Powered by OpenAI Whisper for accurate, real-time transcription
            </p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Full-Text Search
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Search through transcripts to find exactly what you're looking for
            </p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-4">📥</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Export Options
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Download transcripts in TXT, CSV, or JSON formats
            </p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="text-center pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Already have videos?
          </p>
          <button
            onClick={() => navigate('/history')}
            className="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 
                     text-gray-900 dark:text-white font-medium rounded-lg transition-colors"
          >
            View History
          </button>
        </div>
      </div>
    </div>
  );
}
