'use client';

import { useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Task } from '@/lib/types';
import { CountdownDisplay } from './countdown-display';
import { Button } from '@/components/ui/button';
import { Kbd } from '@/components/ui/kbd';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Check, 
  Clock,
  ChevronRight,
  Plus
} from 'lucide-react';

interface FocusViewProps {
  task: Task;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onComplete: () => void;
  onReset: () => void;
  onSnooze: (minutes: number) => void;
  onCompleteSubtask: (subtaskId: string) => void;
  className?: string;
}

const SNOOZE_OPTIONS = [5, 10, 15];

export function FocusView({
  task,
  onStart,
  onPause,
  onResume,
  onComplete,
  onReset,
  onSnooze,
  onCompleteSubtask,
  className
}: FocusViewProps) {
  const currentSubtask = task.subtasks[task.currentSubtaskIndex];
  const completedSubtasks = task.subtasks.filter(s => s.completed).length;
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      switch (e.key.toLowerCase()) {
        case ' ':
          e.preventDefault();
          if (task.status === 'running') onPause();
          else if (task.status === 'paused' || task.status === 'pending') {
            task.status === 'pending' ? onStart() : onResume();
          }
          break;
        case 'enter':
          if (task.status === 'running' || task.status === 'expired') {
            if (currentSubtask && !currentSubtask.completed) {
              onCompleteSubtask(currentSubtask.id);
            } else {
              onComplete();
            }
          }
          break;
        case 'r':
          if (e.metaKey || e.ctrlKey) {
            e.preventDefault();
            onReset();
          }
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [task, onStart, onPause, onResume, onComplete, onReset, currentSubtask, onCompleteSubtask]);
  
  const renderControls = useCallback(() => {
    switch (task.status) {
      case 'pending':
        return (
          <div className="flex items-center gap-3">
            <Button
              size="lg"
              onClick={onStart}
              className="gap-2 px-8"
            >
              <Play className="w-5 h-5" />
              Start
              <Kbd className="ml-2 bg-primary-foreground/20 text-primary-foreground">Space</Kbd>
            </Button>
          </div>
        );
      
      case 'running':
        return (
          <div className="flex items-center gap-3">
            <Button
              size="lg"
              variant="secondary"
              onClick={onPause}
              className="gap-2"
            >
              <Pause className="w-5 h-5" />
              Pause
              <Kbd className="ml-2">Space</Kbd>
            </Button>
            <Button
              size="lg"
              onClick={onComplete}
              className="gap-2 bg-completed hover:bg-completed/90 text-completed-foreground"
            >
              <Check className="w-5 h-5" />
              Complete
              <Kbd className="ml-2 bg-completed-foreground/20 text-completed-foreground">Enter</Kbd>
            </Button>
          </div>
        );
      
      case 'paused':
        return (
          <div className="flex items-center gap-3">
            <Button
              size="lg"
              onClick={onResume}
              className="gap-2 px-8"
            >
              <Play className="w-5 h-5" />
              Resume
              <Kbd className="ml-2 bg-primary-foreground/20 text-primary-foreground">Space</Kbd>
            </Button>
            <Button
              size="lg"
              variant="ghost"
              onClick={onReset}
              className="gap-2 text-muted-foreground"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </Button>
          </div>
        );
      
      case 'expired':
        return (
          <div className="flex flex-col items-center gap-4">
            <div className="flex items-center gap-3">
              <Button
                size="lg"
                onClick={onComplete}
                className="gap-2 bg-completed hover:bg-completed/90 text-completed-foreground"
              >
                <Check className="w-5 h-5" />
                Mark Complete
              </Button>
              <Button
                size="lg"
                variant="ghost"
                onClick={onReset}
                className="gap-2 text-muted-foreground"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground flex items-center gap-1">
                <Plus className="w-3.5 h-3.5" />
                Snooze:
              </span>
              {SNOOZE_OPTIONS.map(mins => (
                <Button
                  key={mins}
                  size="sm"
                  variant="outline"
                  onClick={() => onSnooze(mins * 60)}
                  className="text-xs"
                >
                  +{mins}m
                </Button>
              ))}
            </div>
          </div>
        );
      
      case 'completed':
        return (
          <div className="flex items-center gap-3">
            <Button
              size="lg"
              variant="ghost"
              onClick={onReset}
              className="gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Start Again
            </Button>
          </div>
        );
      
      default:
        return null;
    }
  }, [task.status, onStart, onPause, onResume, onComplete, onReset, onSnooze]);
  
  return (
    <div className={cn(
      'flex flex-col items-center justify-center min-h-[60vh] px-6',
      className
    )}>
      {/* Task title */}
      <h1 className={cn(
        'text-2xl font-semibold text-center mb-2 max-w-xl text-balance',
        task.status === 'completed' && 'text-completed',
        task.status === 'expired' && 'text-expired'
      )}>
        {task.title}
      </h1>
      
      {task.description && (
        <p className="text-muted-foreground text-center mb-8 max-w-md">
          {task.description}
        </p>
      )}
      
      {/* Countdown */}
      <div className="my-12">
        <CountdownDisplay
          elapsed={task.elapsed}
          duration={task.duration}
          status={task.status}
          size="xl"
          showProgress
        />
      </div>
      
      {/* Subtasks progress */}
      {task.subtasks.length > 0 && (
        <div className="w-full max-w-md mb-8">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-muted-foreground">
              Steps Progress
            </span>
            <span className="text-sm font-mono text-muted-foreground">
              {completedSubtasks}/{task.subtasks.length}
            </span>
          </div>
          
          <div className="space-y-2">
            {task.subtasks.map((subtask, index) => {
              const isCurrent = index === task.currentSubtaskIndex;
              const isPast = subtask.completed;
              const isFuture = index > task.currentSubtaskIndex && !subtask.completed;
              
              return (
                <button
                  key={subtask.id}
                  onClick={() => !isPast && (task.status === 'running' || task.status === 'expired') && onCompleteSubtask(subtask.id)}
                  disabled={isPast || task.status === 'pending' || task.status === 'completed'}
                  className={cn(
                    'w-full flex items-center gap-3 p-3 rounded-lg text-left transition-all',
                    isPast && 'bg-completed/10 text-completed',
                    isCurrent && !isPast && 'bg-primary/10 border border-primary/30',
                    isFuture && 'opacity-50 bg-muted/30',
                    (task.status === 'running' || task.status === 'expired') && !isPast && 'hover:bg-accent cursor-pointer'
                  )}
                >
                  <div className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium border',
                    isPast && 'bg-completed border-completed text-completed-foreground',
                    isCurrent && !isPast && 'border-primary text-primary',
                    isFuture && 'border-muted-foreground/30 text-muted-foreground'
                  )}>
                    {isPast ? <Check className="w-3.5 h-3.5" /> : index + 1}
                  </div>
                  <span className={cn(
                    'flex-1 text-sm',
                    isPast && 'line-through'
                  )}>
                    {subtask.title}
                  </span>
                  {isCurrent && !isPast && (task.status === 'running' || task.status === 'expired') && (
                    <ChevronRight className="w-4 h-4 text-primary" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Controls */}
      <div className="mt-4">
        {renderControls()}
      </div>
      
      {/* Status indicator */}
      {task.status !== 'pending' && task.status !== 'completed' && (
        <div className="mt-8 flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="w-4 h-4" />
          <span>
            {task.status === 'running' && 'Focus mode active'}
            {task.status === 'paused' && 'Timer paused'}
            {task.status === 'expired' && 'Time expired - wrap up or extend'}
          </span>
        </div>
      )}
    </div>
  );
}
