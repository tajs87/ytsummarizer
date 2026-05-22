/**
 * Dialog component for creating and sharing timestamp links.
 */

import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Share2, X } from 'lucide-react';
import { useShareLink } from '../hooks/useShareLink';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { CopyButton } from './ui/CopyButton';

interface ShareDialogProps {
  videoId: number;
  startTime: number;
  endTime?: number;
  trigger?: React.ReactNode;
}

export function ShareDialog({
  videoId,
  startTime,
  endTime,
  trigger,
}: ShareDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [expiresInHours, setExpiresInHours] = useState<number | undefined>();
  const { createShareLink, lastCreatedLink, isCreating } = useShareLink(videoId);

  const handleCreate = async () => {
    try {
      const payload: {
        start_time: number;
        end_time?: number;
        title?: string;
        expires_in_hours?: number;
      } = {
        start_time: startTime,
      };

      if (typeof endTime === 'number') payload.end_time = endTime;
      if (title.trim()) payload.title = title.trim();
      if (typeof expiresInHours === 'number') payload.expires_in_hours = expiresInHours;

      await createShareLink(payload);
    } catch (error) {
      console.error('Failed to create share link:', error);
    }
  };

  const fullShareUrl = lastCreatedLink
    ? `${window.location.origin}${lastCreatedLink.share_url}`
    : '';

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-1" />
            Share
          </Button>
        )}
      </Dialog.Trigger>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-6 shadow-lg">
          <Dialog.Title className="text-lg font-semibold mb-4">
            Create Share Link
          </Dialog.Title>

          <Dialog.Description className="text-sm text-gray-600 mb-4">
            Share this timestamp: {startTime.toFixed(1)}s
            {endTime && ` - ${endTime.toFixed(1)}s`}
          </Dialog.Description>

          {!lastCreatedLink ? (
            <div className="space-y-4">
              <Input
                label="Title (Optional)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Key insight at 2:30"
              />

              <Input
                label="Expires in hours (Optional)"
                type="number"
                min="1"
                max="720"
                value={expiresInHours || ''}
                onChange={(e) => setExpiresInHours(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="Leave empty for no expiration"
              />

              <Button
                onClick={handleCreate}
                disabled={isCreating}
                className="w-full"
              >
                {isCreating ? 'Creating...' : 'Create Share Link'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Share URL
                </label>
                <div className="flex gap-2">
                  <Input
                    value={fullShareUrl}
                    readOnly
                    className="font-mono text-xs"
                  />
                  <CopyButton text={fullShareUrl} />
                </div>
              </div>

              <Button
                onClick={() => {
                  setOpen(false);
                  window.open(fullShareUrl, '_blank');
                }}
                variant="outline"
                className="w-full"
              >
                Open Shared Link
              </Button>
            </div>
          )}

          <Dialog.Close asChild>
            <button
              className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
