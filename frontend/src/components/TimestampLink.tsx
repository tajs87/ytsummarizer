/**
 * Clickable timestamp component for video navigation.
 */

import { formatTimestamp } from '../utils/formatTimestamp';

interface TimestampLinkProps {
  timeInSeconds: number;
  onClick?: (timeInSeconds: number) => void;
  className?: string;
}

export function TimestampLink({
  timeInSeconds,
  onClick,
  className = '',
}: TimestampLinkProps) {
  const handleClick = () => {
    onClick?.(timeInSeconds);
  };

  return (
    <button
      onClick={handleClick}
      className={`text-blue-600 hover:text-blue-800 hover:underline font-mono text-sm ${className}`}
      title={`Jump to ${formatTimestamp(timeInSeconds)}`}
    >
      {formatTimestamp(timeInSeconds)}
    </button>
  );
}
