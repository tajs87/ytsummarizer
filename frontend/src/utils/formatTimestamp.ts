/**
 * Timestamp formatting utilities.
 */

/**
 * Format seconds to HH:MM:SS timestamp.
 * @param seconds - Time in seconds
 * @returns Formatted timestamp string
 */
export function formatTimestamp(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts = [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    secs.toString().padStart(2, '0'),
  ];

  return parts.join(':');
}

/**
 * Format seconds to a human-readable duration.
 * @param seconds - Duration in seconds
 * @returns Human-readable duration string
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  }

  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }

  return `${secs}s`;
}

/**
 * Parse timestamp string (HH:MM:SS) to seconds.
 * @param timestamp - Timestamp string in HH:MM:SS format
 * @returns Total seconds
 */
export function parseTimestamp(timestamp: string): number {
  const parts = timestamp.split(':').map(Number);

  if (parts.length === 3) {
    const hours = parts[0] ?? 0;
    const minutes = parts[1] ?? 0;
    const seconds = parts[2] ?? 0;
    return hours * 3600 + minutes * 60 + seconds;
  }

  if (parts.length === 2) {
    const minutes = parts[0] ?? 0;
    const seconds = parts[1] ?? 0;
    return minutes * 60 + seconds;
  }

  return parts[0] ?? 0;
}
