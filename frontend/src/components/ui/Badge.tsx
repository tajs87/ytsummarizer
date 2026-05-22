/**
 * Badge component for status indicators and labels.
 * Supports multiple variants for different contexts.
 */

import { HTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'bg-blue-100 text-blue-800 hover:bg-blue-200',
        secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
        success: 'bg-green-100 text-green-800 hover:bg-green-200',
        warning: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
        danger: 'bg-red-100 text-red-800 hover:bg-red-200',
        outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export type BadgeProps = Record<string, never> & HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
