/**
 * WebSocket hook for real-time progress updates.
 */
import { useEffect, useRef, useState } from 'react';
import type { ProgressUpdate } from '@/types/api';

interface UseProgressWebSocketOptions {
  taskId: string | null;
  onProgress?: (update: ProgressUpdate) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

export function useProgressWebSocket({
  taskId,
  onProgress,
  onComplete,
  onError,
}: UseProgressWebSocketOptions) {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const onProgressRef = useRef(onProgress);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onProgressRef.current = onProgress;
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onProgress, onComplete, onError]);

  useEffect(() => {
    if (!taskId) return;

    const wsUrl = import.meta.env['VITE_WS_URL'] || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/v1/ws/progress/${taskId}`);
    let isIntentionalClose = false;

    ws.onopen = () => {
      setIsConnected(true);
      
      // Send periodic pings to keep connection alive
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000); // Ping every 30 seconds

      // Store interval ID for cleanup
      (ws as any)._pingInterval = pingInterval;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ProgressUpdate | { type: string };

        // Ignore pong responses
        if ('type' in data && data.type === 'pong') {
          return;
        }

        const update = data as ProgressUpdate;
        setProgress(update);

        // Call progress callback
        if (onProgressRef.current) {
          onProgressRef.current(update);
        }

        // Call complete callback if finished
        if (update.status === 'completed' || update.status === 'failed') {
          if (onCompleteRef.current) {
            onCompleteRef.current();
          }

          // Task is terminal; close to avoid reconnect churn.
          isIntentionalClose = true;
          ws.close();
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (event) => {
      if (isIntentionalClose || ws.readyState === WebSocket.CLOSED) {
        return;
      }

      console.error('WebSocket error:', event);
      const error = new Error('WebSocket connection error');
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      
      // Clear ping interval
      if ((ws as any)._pingInterval) {
        clearInterval((ws as any)._pingInterval);
      }
    };

    // Cleanup on unmount
    return () => {
      isIntentionalClose = true;
      if ((ws as any)._pingInterval) {
        clearInterval((ws as any)._pingInterval);
      }
      ws.close();
    };
  }, [taskId]);

  return {
    progress,
    isConnected,
  };
}
