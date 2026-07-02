import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines Tailwind classes conditionally, handling conflicts properly.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
