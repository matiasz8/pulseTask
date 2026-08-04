'use client';

import { cn } from '@/lib/utils';
import { TaskCreator } from './task-creator';
import { Clock, Target, Zap } from 'lucide-react';

interface IdleStateProps {
  onCreateTask: (title: string, duration: number, subtasks?: SubtaskWithTime[], autoStart?: boolean) => void;
  className?: string;
}

interface SubtaskWithTime {
  title: string;
  duration: number;
}

export function IdleState({ onCreateTask, className }: IdleStateProps) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center min-h-[70vh] px-6',
      className
    )}>
      <div className="text-center mb-12">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6">
          <Clock className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-semibold mb-3 text-balance">
          Ready to focus
        </h1>
        <p className="text-muted-foreground max-w-md mx-auto text-balance">
          Create a task with a fixed duration. The countdown keeps you accountable.
        </p>
      </div>
      
      <div className="w-full max-w-md">
        <TaskCreator onCreateTask={onCreateTask} />
      </div>
      
      {/* Quick tips */}
      <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
        <div className="flex items-start gap-3 p-4 rounded-xl bg-surface-1/50">
          <div className="w-8 h-8 rounded-lg bg-running/10 flex items-center justify-center flex-shrink-0">
            <Zap className="w-4 h-4 text-running" />
          </div>
          <div>
            <h3 className="text-sm font-medium mb-1">Duration-first</h3>
            <p className="text-xs text-muted-foreground">
              Set your time budget before you start. Work expands to fill available time.
            </p>
          </div>
        </div>
        
        <div className="flex items-start gap-3 p-4 rounded-xl bg-surface-1/50">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Target className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-medium mb-1">Visible pressure</h3>
            <p className="text-xs text-muted-foreground">
              The countdown creates urgency without stress. Execute, don&apos;t procrastinate.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
