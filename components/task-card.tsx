'use client';

import { cn } from '@/lib/utils';
import { Task, TaskStatus } from '@/lib/types';
import { Clock, Check, AlertCircle, Pause, Archive, Play } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  isActive?: boolean;
  onStart?: () => void;
  onClick?: () => void;
  className?: string;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  if (mins >= 60) {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}h ${remainingMins}m`;
  }
  return `${mins}m`;
}

const statusConfig: Record<TaskStatus, { 
  icon: typeof Clock; 
  label: string; 
  className: string;
  bgClassName: string;
}> = {
  pending: { 
    icon: Clock, 
    label: 'Pending', 
    className: 'text-muted-foreground',
    bgClassName: 'bg-muted/50'
  },
  running: { 
    icon: Play, 
    label: 'Running', 
    className: 'text-running',
    bgClassName: 'bg-running/10 border-running/30'
  },
  paused: { 
    icon: Pause, 
    label: 'Paused', 
    className: 'text-paused',
    bgClassName: 'bg-paused/10 border-paused/30'
  },
  expired: { 
    icon: AlertCircle, 
    label: 'Expired', 
    className: 'text-expired',
    bgClassName: 'bg-expired/10 border-expired/30'
  },
  completed: { 
    icon: Check, 
    label: 'Completed', 
    className: 'text-completed',
    bgClassName: 'bg-completed/10 border-completed/30'
  },
  archived: { 
    icon: Archive, 
    label: 'Archived', 
    className: 'text-archived',
    bgClassName: 'bg-archived/10 border-archived/30'
  }
};

export function TaskCard({ task, isActive, onStart, onClick, className }: TaskCardProps) {
  const config = statusConfig[task.status];
  const StatusIcon = config.icon;
  const progress = task.duration > 0 ? (task.elapsed / task.duration) * 100 : 0;
  const completedSubtasks = task.subtasks.filter(s => s.completed).length;
  
  return (
    <button
      onClick={onClick || onStart}
      className={cn(
        'w-full text-left rounded-xl border p-4 transition-all duration-200',
        'hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        isActive ? config.bgClassName : 'bg-card border-border hover:border-border/80',
        className
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className={cn(
            'font-medium truncate',
            task.status === 'completed' && 'line-through opacity-70',
            task.status === 'archived' && 'opacity-50'
          )}>
            {task.title}
          </h3>
          
          {task.description && (
            <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
              {task.description}
            </p>
          )}
          
          <div className="flex items-center gap-3 mt-2">
            <span className={cn('flex items-center gap-1.5 text-xs font-medium', config.className)}>
              <StatusIcon className="w-3.5 h-3.5" />
              {config.label}
            </span>
            
            <span className="text-xs text-muted-foreground font-mono">
              {formatDuration(task.duration)}
            </span>
            
            {task.subtasks.length > 0 && (
              <span className="text-xs text-muted-foreground">
                {completedSubtasks}/{task.subtasks.length} steps
              </span>
            )}
          </div>
        </div>
        
        {(task.status === 'running' || task.status === 'paused' || task.status === 'expired') && (
          <div className="flex-shrink-0">
            <div className="w-12 h-12 rounded-lg bg-surface-1 flex items-center justify-center">
              <span className={cn(
                'font-mono text-sm font-bold',
                config.className
              )}>
                {Math.max(0, Math.floor((task.duration - task.elapsed) / 60))}m
              </span>
            </div>
          </div>
        )}
      </div>
      
      {/* Progress indicator for active tasks */}
      {(task.status === 'running' || task.status === 'paused' || task.status === 'expired') && (
        <div className="mt-3">
          <div className="h-1 bg-muted rounded-full overflow-hidden">
            <div 
              className={cn(
                'h-full rounded-full transition-all',
                task.status === 'expired' ? 'bg-expired' : 
                task.status === 'paused' ? 'bg-paused' : 'bg-running'
              )}
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>
      )}
    </button>
  );
}
