import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { VideoInput } from '@/components/VideoInput';

const mutateAsync = vi.fn();

vi.mock('@/services/videos', () => ({
  useSubmitVideo: () => ({
    mutateAsync,
    isPending: false,
    isError: false,
    error: null,
  }),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe('VideoInput', () => {
  beforeEach(() => {
    mutateAsync.mockReset();
  });

  it('submits valid youtube url and calls onSubmitSuccess', async () => {
    mutateAsync.mockResolvedValue({ id: 42 });
    const onSubmitSuccess = vi.fn();

    renderWithProviders(<VideoInput onSubmitSuccess={onSubmitSuccess} />);

    fireEvent.change(screen.getByLabelText('Video URL'), {
      target: { value: 'https://www.youtube.com/watch?v=jNQXAC9IVRw' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Start Transcription' }));

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledTimes(1);
      expect(onSubmitSuccess).toHaveBeenCalledWith(42);
    });
  });

  it('shows validation error for unsupported url', () => {
    renderWithProviders(<VideoInput />);

    fireEvent.change(screen.getByLabelText('Video URL'), {
      target: { value: 'https://example.com/page' },
    });

    expect(
      screen.getByText('Unsupported video URL. Use YouTube, Vimeo, or direct video file URL.')
    ).toBeInTheDocument();
  });
});
