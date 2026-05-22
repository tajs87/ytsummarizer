/**
 * Home page.
 * Main landing page with video submission form.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { VideoInput } from '@/components/VideoInput';
import { ProgressTracker } from '@/components/ProgressTracker';
import { useVideo } from '@/services/videos';
import { useAuth } from '@/hooks/useAuth';

export function Home() {
  const [submittedVideoId, setSubmittedVideoId] = useState<number | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [showAuthPanel, setShowAuthPanel] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { data: video } = useVideo(submittedVideoId);
  const { user, isLoading, isAuthenticated, migratedItems, login, register, logout } = useAuth();

  const handleSubmitSuccess = (videoId: number) => {
    setSubmittedVideoId(videoId);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);

    try {
      if (isRegisterMode) {
        await register(email.trim(), password);
      } else {
        await login(email.trim(), password);
      }
      setPassword('');
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Authentication failed');
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

        {isLoading ? (
          <div className="max-w-2xl mx-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 text-center text-gray-600 dark:text-gray-300">
            Loading account...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="max-w-2xl mx-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 flex items-center justify-between">
              {isAuthenticated ? (
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Signed in as <span className="font-medium">{user?.email}</span>
                </p>
              ) : (
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Guest mode active. Your history is temporary for this browser session.
                </p>
              )}
              {isAuthenticated ? (
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-md"
                >
                  Logout
                </button>
              ) : (
                <button
                  onClick={() => { setShowAuthPanel((prev) => !prev); }}
                  className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
                >
                  {showAuthPanel ? 'Hide Login' : 'Save Permanently'}
                </button>
              )}
            </div>

            {isAuthenticated && migratedItems > 0 && (
              <div className="max-w-2xl mx-auto rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-4 text-sm text-green-800 dark:text-green-200">
                {migratedItems} guest item{migratedItems === 1 ? '' : 's'} migrated to your account history.
              </div>
            )}

            {/* Video submission form */}
            <VideoInput onSubmitSuccess={handleSubmitSuccess} />

            {!isAuthenticated && !showAuthPanel && (
              <div className="max-w-2xl mx-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Want to keep your guest history after this session?
                </p>
                <button
                  onClick={() => { setShowAuthPanel(true); }}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                >
                  Save Permanently
                </button>
              </div>
            )}

            {!isAuthenticated && showAuthPanel && (
              <div className="max-w-2xl mx-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Save your history permanently
                </h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {isRegisterMode
                    ? 'Create an account to keep your guest work.'
                    : 'Sign in to migrate guest items and keep permanent history.'}
                </p>

                <form onSubmit={handleAuthSubmit} className="mt-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => { setEmail(e.target.value); }}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Password
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => { setPassword(e.target.value); }}
                      minLength={8}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  {authError && (
                    <div className="p-3 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 text-sm text-red-700 dark:text-red-300">
                      {authError}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    {isRegisterMode ? 'Create Account' : 'Sign In'}
                  </button>
                </form>

                <button
                  onClick={() => {
                    setIsRegisterMode((prev) => !prev);
                    setAuthError(null);
                  }}
                  className="mt-4 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  {isRegisterMode ? 'Already have an account? Sign in' : "Don't have an account? Create one"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Progress tracker */}
        {video?.task_id && video.status !== 'COMPLETED' && (
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
                  {video.title ?? 'Your video'} has been transcribed successfully
                </p>
              </div>
              <Link
                to={`/video/${video.id}`}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
              >
                View Transcription
              </Link>
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
              Search through transcripts to find exactly what you&apos;re looking for
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
            onClick={() => { navigate('/history'); }}
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
