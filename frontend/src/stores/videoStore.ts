/**
 * Video state management store using Zustand.
 * Manages video processing state, current video, and progress tracking.
 */

import { create } from 'zustand';
import { Video, VideoStatus } from '../types/video';

type VideoState = {
  currentVideo: Video | null;
  processingVideos: Map<number, { progress: number; status: VideoStatus }>;

  setCurrentVideo: (video: Video | null) => void;
  updateVideoStatus: (videoId: number, status: VideoStatus) => void;
  updateVideoProgress: (videoId: number, progress: number) => void;
  addProcessingVideo: (videoId: number) => void;
  removeProcessingVideo: (videoId: number) => void;
  clearProcessingVideos: () => void;
};

export const useVideoStore = create<VideoState>((set) => ({
  currentVideo: null,
  processingVideos: new Map(),

  setCurrentVideo: (video) => {
    set({ currentVideo: video });
  },

  updateVideoStatus: (videoId, status) => {
    set((state) => {
      const processingVideos = new Map(state.processingVideos);
      const existing = processingVideos.get(videoId);
      if (existing) {
        processingVideos.set(videoId, { ...existing, status });
      }
      return { processingVideos };
    });
  },

  updateVideoProgress: (videoId, progress) => {
    set((state) => {
      const processingVideos = new Map(state.processingVideos);
      const existing = processingVideos.get(videoId);
      if (existing) {
        processingVideos.set(videoId, { ...existing, progress });
      }
      return { processingVideos };
    });
  },

  addProcessingVideo: (videoId) => {
    set((state) => {
      const processingVideos = new Map(state.processingVideos);
      processingVideos.set(videoId, { progress: 0, status: 'PENDING' });
      return { processingVideos };
    });
  },

  removeProcessingVideo: (videoId) => {
    set((state) => {
      const processingVideos = new Map(state.processingVideos);
      processingVideos.delete(videoId);
      return { processingVideos };
    });
  },

  clearProcessingVideos: () => {
    set({ processingVideos: new Map() });
  },
}));
