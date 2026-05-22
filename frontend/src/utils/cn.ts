/**
 * Utility for merging Tailwind CSS class names with proper precedence.
 * Combines clsx and tailwind-merge for optimal class name handling.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
