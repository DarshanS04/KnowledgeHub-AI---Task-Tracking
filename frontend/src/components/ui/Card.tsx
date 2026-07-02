import React from 'react';
import { cn } from '../../utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

export const Card: React.FC<CardProps> = ({ className, glass = true, children, ...props }) => {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-800 bg-slate-900/40 p-6 shadow-xl',
        glass && 'glass-card',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
