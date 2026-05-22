/**
 * Public share page for viewing shared video content.
 */

import { useParams } from 'react-router-dom';
import { AlertCircle, Clock } from 'lucide-react';
import { useSharedContent } from '../services/shares';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { TimestampLink } from '../components/TimestampLink';

export function SharePage() {
  const { token } = useParams<{ token: string }>();
  const { data, isLoading, error } = useSharedContent(token ?? '');

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
          <p className="mt-4 text-gray-600">Loading shared content...</p>
        </div>
      </div>
    );
  }

  // eslint-disable-next-line @typescript-eslint/prefer-nullish-coalescing
  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Share Link Not Found</h2>
              <p className="text-gray-600">
                This share link may be invalid, expired, or no longer active.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>{data.title ?? data.video_title ?? 'Shared Video Segment'}</CardTitle>
            <div className="flex items-center text-sm text-gray-600 mt-2">
              <Clock className="h-4 w-4 mr-1" />
              <span>Timestamp: </span>
              <TimestampLink
                timeInSeconds={data.start_time}
                className="ml-1"
              />
              {data.end_time && (
                <>
                  <span className="mx-1">-</span>
                  <TimestampLink timeInSeconds={data.end_time} />
                </>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <h3 className="font-medium mb-3">Transcription</h3>
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
              {data.transcription_text}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
