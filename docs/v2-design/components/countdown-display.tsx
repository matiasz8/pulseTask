'use client';

import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { TaskStatus } from '@/lib/types';

interface CountdownDisplayProps {
  elapsed: number;
  duration: number;
  status: TaskStatus;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showProgress?: boolean;
  className?: string;
}

function formatTime(seconds: number): { minutes: string; secs: string; isNegative: boolean } {
  const isNegative = seconds < 0;
  const absSeconds = Math.abs(seconds);
  const mins = Math.floor(absSeconds / 60);
  const secs = absSeconds % 60;
  return {
    minutes: mins.toString().padStart(2, '0'),
    secs: secs.toString().padStart(2, '0'),
    isNegative
  };
}

export function CountdownDisplay({
  elapsed,
  duration,
  status,
  size = 'lg',
  showProgress = true,
  className
}: CountdownDisplayProps) {
  const remaining = duration - elapsed;
  const { minutes, secs, isNegative } = formatTime(remaining);
  const progress = Math.min((elapsed / duration) * 100, 100);
  const overtime = elapsed - duration;
  
  const sizeClasses = {
    sm: 'text-2xl',
    md: 'text-4xl',
    lg: 'text-6xl',
    xl: 'text-8xl'
  };
  
  const statusStyles = useMemo(() => {
    switch (status) {
      case 'running':
        return 'text-running';
      case 'paused':
        return 'text-paused';
      case 'expired':
        return 'text-expired';
      case 'completed':
        return 'text-completed';
      case 'pending':
        return 'text-muted-foreground';
      case 'archived':
        return 'text-archived';
      default:
        return 'text-foreground';
    }
  }, [status]);
  
  const progressBarColor = useMemo(() => {
    if (status === 'expired') return 'bg-expired';
    if (status === 'completed') return 'bg-completed';
    if (status === 'paused') return 'bg-paused';
    if (progress > 90) return 'bg-expired/70';
    if (progress > 75) return 'bg-paused';
    return 'bg-running';
  }, [status, progress]);
  
  return (
    <div className={cn('flex flex-col items-center gap-4', className)}>
      <div className={cn(
        'font-mono font-bold tracking-tight countdown-display',
        sizeClasses[size],
        statusStyles,
        status === 'expired' && 'animate-pulse'
      )}>
        <span className="opacity-80">{isNegative ? '-' : ''}</span>
        <span>{minutes}</span>
        <span className={cn(
          'mx-1',
          status === 'running' && 'animate-pulse'
        )}>:</span>
        <span>{secs}</span>
      </div>
      
      {status === 'expired' && overtime > 0 && (
        <div className="text-sm font-mono text-expired/80">
          +{formatTime(overtime).minutes}:{formatTime(overtime).secs} overtime
        </div>
      )}
      
      {showProgress && (
        <div className="w-full max-w-md">
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div 
              className={cn(
                'h-full transition-all duration-1000 ease-linear rounded-full',
                progressBarColor
              )}
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-muted-foreground font-mono">
            <span>{formatTime(elapsed).minutes}:{formatTime(elapsed).secs}</span>
            <span>{formatTime(duration).minutes}:{formatTime(duration).secs}</span>
          </div>
        </div>
      )}
    </div>
  );
}
