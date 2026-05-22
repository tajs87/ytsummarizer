/**
 * URL validation utilities.
 */

/**
 * Check if a string is a valid URL.
 */
export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Check if URL is a YouTube video.
 */
export function isYouTubeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return (
      parsed.hostname === 'www.youtube.com' ||
      parsed.hostname === 'youtube.com' ||
      parsed.hostname === 'youtu.be' ||
      parsed.hostname === 'm.youtube.com'
    );
  } catch {
    return false;
  }
}

/**
 * Check if URL is a Vimeo video.
 */
export function isVimeoUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.hostname === 'vimeo.com' || parsed.hostname === 'www.vimeo.com';
  } catch {
    return false;
  }
}

/**
 * Check if URL appears to be a direct video link.
 */
export function isDirectVideoUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'];
    const path = parsed.pathname.toLowerCase();

    return videoExtensions.some((ext) => path.endsWith(ext));
  } catch {
    return false;
  }
}

/**
 * Extract video ID from YouTube URL.
 */
export function extractYouTubeId(url: string): string | null {
  try {
    const parsed = new URL(url);

    // youtu.be format
    if (parsed.hostname === 'youtu.be') {
      return parsed.pathname.slice(1);
    }

    // youtube.com/watch?v= format
    if (parsed.hostname.includes('youtube.com')) {
      return parsed.searchParams.get('v');
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Extract video ID from Vimeo URL.
 */
export function extractVimeoId(url: string): string | null {
  try {
    const parsed = new URL(url);
    const match = parsed.pathname.match(/\/(\d+)/);
    return match?.[1] ?? null;
  } catch {
    return null;
  }
}

/**
 * Validate and normalize video URL.
 */
export function validateVideoUrl(url: string): {
  isValid: boolean;
  platform?: 'youtube' | 'vimeo' | 'direct';
  videoId?: string;
  error?: string;
} {
  if (!url.trim()) {
    return { isValid: false, error: 'URL is required' };
  }

  if (!isValidUrl(url)) {
    return { isValid: false, error: 'Invalid URL format' };
  }

  if (isYouTubeUrl(url)) {
    const videoId = extractYouTubeId(url);
    if (!videoId) {
      return { isValid: false, error: 'Could not extract YouTube video ID' };
    }
    return { isValid: true, platform: 'youtube', videoId };
  }

  if (isVimeoUrl(url)) {
    const videoId = extractVimeoId(url);
    if (!videoId) {
      return { isValid: false, error: 'Could not extract Vimeo video ID' };
    }
    return { isValid: true, platform: 'vimeo', videoId };
  }

  // Validate direct video URL
  if (isDirectVideoUrl(url)) {
    return { isValid: true, platform: 'direct' };
  }

  return { isValid: false, error: 'Unsupported video URL. Use YouTube, Vimeo, or direct video file URL.' };
}
