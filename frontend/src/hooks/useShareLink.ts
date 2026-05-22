/**
 * Hook for creating and managing share links.
 */

import { useState } from 'react';
import { useCreateShareLink } from '../services/shares';
import { ShareLinkRequest, ShareLinkResponse } from '../types/share';

export function useShareLink(videoId: number) {
  const [lastCreatedLink, setLastCreatedLink] = useState<ShareLinkResponse | null>(null);
  const createShareMutation = useCreateShareLink(videoId);

  const createShareLink = async (data: ShareLinkRequest) => {
    const result = await createShareMutation.mutateAsync(data);
    setLastCreatedLink(result);
    return result;
  };

  const copyShareLink = async (link: string) => {
    try {
      await navigator.clipboard.writeText(link);
      return true;
    } catch (error) {
      console.error('Failed to copy link:', error);
      return false;
    }
  };

  return {
    createShareLink,
    copyShareLink,
    lastCreatedLink,
    isCreating: createShareMutation.isPending,
    error: createShareMutation.error,
  };
}
