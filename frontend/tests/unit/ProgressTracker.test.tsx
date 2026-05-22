import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { ProgressTracker } from '@/components/ProgressTracker';

vi.mock('@/hooks/useProgressWebSocket', () => ({
  useProgressWebSocket: () => ({
    progress: {
      progress: 60,
      message: 'Transcribing...',
      status: 'processing',
    },
    isConnected: true,
  }),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe('ProgressTracker', () => {
  it('shows progress percent and status text', () => {
    renderWithProviders(<ProgressTracker taskId="task-1" videoId={1} />);

    expect(screen.getByText('Processing Video')).toBeInTheDocument();
    expect(screen.getByText('Transcribing...')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('renders nothing when taskId is null', () => {
    const { container } = renderWithProviders(<ProgressTracker taskId={null} videoId={1} />);
    expect(container).toBeEmptyDOMElement();
  });
});
