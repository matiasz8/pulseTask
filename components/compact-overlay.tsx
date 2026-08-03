'use client';

import { cn } from '@/lib/utils';
import { Task } from '@/lib/types';
import { CountdownDisplay } from './countdown-display';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  Check,
  Minimize2,
  Maximize2,
  X
} from 'lucide-react';

type OverlayMode = 'normal' | 'compact' | 'ultracompact';

interface CompactOverlayProps {
  task: Task | null;
  mode: OverlayMode;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onComplete: () => void;
  onModeChange: (mode: OverlayMode) => void;
  onClose: () => void;
  className?: string;
}

export function CompactOverlay({
  task,
  mode,
  onStart,
  onPause,
  onResume,
  onComplete,
  onModeChange,
  onClose,
  className
}: CompactOverlayProps) {
  if (!task) {
    return (
      <div className={cn(
        'rounded-xl bg-card border border-border shadow-lg p-4',
        'flex items-center justify-center gap-3',
        className
      )}>
        <span className="text-sm text-muted-foreground">No active task</span>
        <Button size="sm" variant="ghost" onClick={onClose}>
          <X className="w-4 h-4" />
        </Button>
      </div>
    );
  }
  
  const handlePlayPause = () => {
    if (task.status === 'running') {
      onPause();
    } else if (task.status === 'paused') {
      onResume();
    } else if (task.status === 'pending') {
      onStart();
    }
  };
  
  // Ultra-compact: just time and one button
  if (mode === 'ultracompact') {
    return (
      <div className={cn(
        'rounded-lg bg-card/95 backdrop-blur border border-border shadow-lg',
        'flex items-center gap-2 px-3 py-2',
        task.status === 'expired' && 'border-expired/50 bg-expired/10',
        className
      )}>
        <CountdownDisplay
          elapsed={task.elapsed}
          duration={task.duration}
          status={task.status}
          size="sm"
          showProgress={false}
          className="flex-row gap-0"
        />
        <button
          onClick={handlePlayPause}
          className={cn(
            'w-7 h-7 rounded-md flex items-center justify-center transition-colors',
            task.status === 'running' 
              ? 'bg-secondary hover:bg-secondary/80' 
              : 'bg-primary hover:bg-primary/90'
          )}
        >
          {task.status === 'running' ? (
            <Pause className="w-3.5 h-3.5 text-secondary-foreground" />
          ) : (
            <Play className="w-3.5 h-3.5 text-primary-foreground" />
          )}
        </button>
        <button
          onClick={() => onModeChange('compact')}
          className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <Maximize2 className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }
  
  // Compact: time, title, controls
  if (mode === 'compact') {
    return (
      <div className={cn(
        'rounded-xl bg-card/95 backdrop-blur border border-border shadow-lg',
        'w-72 p-4',
        task.status === 'expired' && 'border-expired/50 bg-expired/10',
        className
      )}>
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-medium text-sm truncate flex-1 pr-2">
            {task.title}
          </h3>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onModeChange('ultracompact')}
              className="w-6 h-6 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              <Minimize2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onModeChange('normal')}
              className="w-6 h-6 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onClose}
              className="w-6 h-6 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        
        <CountdownDisplay
          elapsed={task.elapsed}
          duration={task.duration}
          status={task.status}
          size="md"
          showProgress
        />
        
        <div className="flex items-center gap-2 mt-4">
          <Button
            size="sm"
            variant={task.status === 'running' ? 'secondary' : 'default'}
            onClick={handlePlayPause}
            className="flex-1"
          >
            {task.status === 'running' ? (
              <>
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-1" />
                {task.status === 'paused' ? 'Resume' : 'Start'}
              </>
            )}
          </Button>
          {(task.status === 'running' || task.status === 'expired') && (
            <Button
              size="sm"
              onClick={onComplete}
              className="bg-completed hover:bg-completed/90 text-completed-foreground"
            >
              <Check className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    );
  }
  
  // Normal overlay: full info
  return (
    <div className={cn(
      'rounded-xl bg-card/95 backdrop-blur border border-border shadow-xl',
      'w-80 p-5',
      task.status === 'expired' && 'border-expired/50',
      className
    )}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 pr-4">
          <h3 className="font-semibold truncate">
            {task.title}
          </h3>
          {task.description && (
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {task.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onModeChange('compact')}
            className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <CountdownDisplay
        elapsed={task.elapsed}
        duration={task.duration}
        status={task.status}
        size="lg"
        showProgress
      />
      
      {/* Subtask progress */}
      {task.subtasks.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
            <span>Current step</span>
            <span>{task.subtasks.filter(s => s.completed).length}/{task.subtasks.length}</span>
          </div>
          {task.subtasks[task.currentSubtaskIndex] && (
            <p className="text-sm font-medium">
              {task.subtasks[task.currentSubtaskIndex].title}
            </p>
          )}
        </div>
      )}
      
      <div className="flex items-center gap-2 mt-5">
        <Button
          size="sm"
          variant={task.status === 'running' ? 'secondary' : 'default'}
          onClick={handlePlayPause}
          className="flex-1"
        >
          {task.status === 'running' ? (
            <>
              <Pause className="w-4 h-4 mr-2" />
              Pause
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              {task.status === 'paused' ? 'Resume' : 'Start'}
            </>
          )}
        </Button>
        {(task.status === 'running' || task.status === 'expired') && (
          <Button
            size="sm"
            onClick={onComplete}
            className="bg-completed hover:bg-completed/90 text-completed-foreground"
          >
            <Check className="w-4 h-4 mr-2" />
            Done
          </Button>
        )}
      </div>
    </div>
  );
}
