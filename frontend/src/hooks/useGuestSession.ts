import { useEffect } from 'react';

import { apiClient } from '@/services/api';

export function useGuestSession(isAuthenticated: boolean): void {
  useEffect(() => {
    if (isAuthenticated) {
      return;
    }

    void apiClient.post('/api/v1/guest/session').catch(() => {
      // Guest bootstrap failures should not block initial page render.
    });
  }, [isAuthenticated]);
}
