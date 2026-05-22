import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { Home } from '@/pages/Home';

const mutateAsync = vi.fn();

vi.mock('@/services/videos', () => ({
  useSubmitVideo: () => ({
    mutateAsync,
    isPending: false,
    isError: false,
    error: null,
  }),
  useVideo: () => ({
    data: {
      id: 1,
      url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
      platform: 'YOUTUBE',
      title: 'Test Video',
      duration_seconds: 19,
      status: 'COMPLETED',
      error_message: null,
      task_id: null,
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      has_transcription: true,
    },
    isLoading: false,
    error: null,
  }),
}));

vi.mock('@/components/ProgressTracker', () => ({
  ProgressTracker: () => <div>ProgressTracker</div>,
}));

function renderApp() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe('video submission integration', () => {
  it('submits URL from home page flow', async () => {
    mutateAsync.mockResolvedValue({ id: 1 });

    renderApp();

    fireEvent.change(screen.getByLabelText('Video URL'), {
      target: { value: 'https://www.youtube.com/watch?v=jNQXAC9IVRw' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Start Transcription' }));

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith({
        url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
      });
    });

    expect(screen.getByText('✓ Transcription Complete')).toBeInTheDocument();
  });
});
