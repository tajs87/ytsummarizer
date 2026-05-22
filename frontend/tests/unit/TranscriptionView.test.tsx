import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { TranscriptionView } from '@/components/TranscriptionView';

const mutateAsync = vi.fn();

vi.mock('@/services/transcriptions', () => ({
  useSearchTranscription: () => ({
    mutateAsync,
    isPending: false,
    data: null,
    reset: vi.fn(),
  }),
  exportTranscription: vi.fn().mockResolvedValue('exported text'),
}));

vi.mock('@/components/ShareDialog', () => ({
  ShareDialog: () => <button type="button">Share</button>,
}));

const transcription = {
  id: 1,
  video_id: 1,
  full_text: 'hello world from transcript',
  segments: [
    { id: 0, start: 0, end: 2, text: 'hello world' },
    { id: 1, start: 2, end: 4, text: 'from transcript' },
  ],
  language: 'en',
  word_count: 4,
  processing_time_seconds: 1,
  created_at: new Date().toISOString(),
};

describe('TranscriptionView', () => {
  it('renders segment content and metadata', () => {
    render(<TranscriptionView transcription={transcription} videoTitle="Demo" />);

    expect(screen.getByText('Demo')).toBeInTheDocument();
    expect(screen.getByText('hello world')).toBeInTheDocument();
    expect(screen.getByText('from transcript')).toBeInTheDocument();
  });

  it('runs search mutation when submitting search form', () => {
    render(<TranscriptionView transcription={transcription} videoTitle="Demo" />);

    fireEvent.change(screen.getByPlaceholderText('Search within transcription...'), {
      target: { value: 'hello' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));

    expect(mutateAsync).toHaveBeenCalledWith({ query: 'hello' });
  });
});
