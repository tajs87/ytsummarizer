/**
 * History page.
 * Shows list of user's videos with filtering and status.
 */
import { Link } from 'react-router-dom';
import { VideoList } from '@/components/VideoList';
import { useAuth } from '@/hooks/useAuth';

export function History() {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-16 text-gray-600 dark:text-gray-300">
            Loading account...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {isAuthenticated ? 'Video History' : 'Guest Session History'}
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {isAuthenticated
                ? 'View and manage your transcribed videos'
                : 'Guest history is session-only and clears when your browser session ends'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="px-5 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-medium rounded-lg transition-colors"
            >
              Back to Home
            </Link>
            <Link
              to="/"
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              + New Video
            </Link>
          </div>
        </div>

        {/* Video list */}
        <VideoList />
      </div>
    </div>
  );
}
