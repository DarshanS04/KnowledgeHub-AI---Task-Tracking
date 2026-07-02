import React from 'react';
import { cn } from '../../utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:pointer-events-none disabled:opacity-50',
          {
            // Variants
            'bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800 shadow-lg shadow-indigo-600/20':
              variant === 'primary',
            'bg-slate-800 text-slate-100 hover:bg-slate-700 active:bg-slate-600':
              variant === 'secondary',
            'border border-slate-700 bg-transparent text-slate-300 hover:bg-slate-800 hover:text-white':
              variant === 'outline',
            'text-slate-400 hover:bg-slate-800 hover:text-white':
              variant === 'ghost',
            'bg-rose-600 text-white hover:bg-rose-700 active:bg-rose-800 shadow-lg shadow-rose-600/20':
              variant === 'danger',

            // Sizes
            'h-9 px-3 text-sm': size === 'sm',
            'h-10 px-4 py-2 text-sm': size === 'md',
            'h-11 px-6 text-base': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="mr-2 h-4 w-4 animate-spin text-current"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
