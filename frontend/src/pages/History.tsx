/**
 * History page.
 * Shows list of user's videos with filtering and status.
 */
import { Link } from 'react-router-dom';
import { VideoList } from '@/components/VideoList';

export function History() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Video History
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              View and manage your transcribed videos
            </p>
          </div>
          <Link
            to="/"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            + New Video
          </Link>
        </div>

        {/* Video list */}
        <VideoList />
      </div>
    </div>
  );
}
