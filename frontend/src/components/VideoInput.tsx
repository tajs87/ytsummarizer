/**
 * VideoInput component.
 * Allows users to submit YouTube/Vimeo URLs for transcription.
 */
import { useState } from 'react';
import { useSubmitVideo } from '@/services/videos';
import { validateVideoUrl } from '@/utils/validators';

type VideoInputProps = {
  onSubmitSuccess?: (videoId: number) => void;
}

export function VideoInput({ onSubmitSuccess }: VideoInputProps) {
  const [url, setUrl] = useState('');
  const submitVideo = useSubmitVideo();
  const validation = validateVideoUrl(url);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim() || !validation.isValid) {
      return;
    }

    try {
      const video = await submitVideo.mutateAsync({ url: url.trim() });
      
      // Clear input
      setUrl('');

      // Notify parent
      if (onSubmitSuccess) {
        onSubmitSuccess(video.id);
      }
    } catch (error) {
      console.error('Failed to submit video:', error);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="video-url"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Video URL
          </label>
          <input
            id="video-url"
            type="url"
            value={url}
            onChange={(e) => { setUrl(e.target.value); }}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     dark:bg-gray-800 dark:text-white
                     disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={submitVideo.isPending}
            required
          />
          {url.trim() && !validation.isValid && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">{validation.error}</p>
          )}
          {url.trim() && validation.isValid && validation.platform && (
            <p className="mt-2 text-sm text-green-700 dark:text-green-400">
              Detected platform: {validation.platform === 'youtube' ? 'YouTube' : validation.platform === 'vimeo' ? 'Vimeo' : 'Direct video'}
            </p>
          )}
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Supported: YouTube, Vimeo, or direct video links (.mp4, .mov, .webm)
          </p>
          <div className="mt-2 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            <span>YouTube</span>
            <span>Vimeo</span>
            <span>Direct URL</span>
          </div>
        </div>

        {submitVideo.isError && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-800 dark:text-red-200">
              {submitVideo.error instanceof Error
                ? submitVideo.error.message
                : 'Failed to submit video. Please try again.'}
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={submitVideo.isPending || !url.trim() || !validation.isValid}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 
                   text-white font-medium rounded-lg
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors duration-200"
        >
          {submitVideo.isPending ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
              Submitting...
            </span>
          ) : (
            'Start Transcription'
          )}
        </button>
      </form>
    </div>
  );
}
