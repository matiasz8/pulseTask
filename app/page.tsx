'use client';

import { useEffect, useCallback, useRef } from 'react';
import { useTaskStore } from '@/lib/store';
import type { SubtaskWithTime } from '@/lib/store';
import { AppHeader } from '@/components/app-header';
import { FocusView } from '@/components/focus-view';
import { IdleState } from '@/components/idle-state';
import { TaskList } from '@/components/task-list';
import { StatsDashboard } from '@/components/stats-dashboard';
import { SettingsPanel } from '@/components/settings-panel';
import { CompactOverlay } from '@/components/compact-overlay';
import { cn } from '@/lib/utils';

export default function PulseTaskApp() {
  const {
    tasks,
    activeTaskId,
    viewMode,
    overlayMode,
    isOverlayVisible,
    addTask,
    startTask,
    viewTask,
    pauseTask,
    resumeTask,
    completeTask,
    resetTask,
    snoozeTask,
    completeSubtask,
    tick,
    setViewMode,
    setOverlayMode,
    toggleOverlay,
    getActiveTask,
    getMetrics
  } = useTaskStore();
  
  const activeTask = getActiveTask();
  const metrics = getMetrics();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Timer tick
  useEffect(() => {
    if (activeTask?.status === 'running') {
      intervalRef.current = setInterval(tick, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [activeTask?.status, tick]);
  
  // Update document title with countdown
  useEffect(() => {
    if (activeTask && ['running', 'paused', 'expired'].includes(activeTask.status)) {
      const remaining = activeTask.duration - activeTask.elapsed;
      const mins = Math.floor(Math.abs(remaining) / 60);
      const secs = Math.abs(remaining) % 60;
      const sign = remaining < 0 ? '-' : '';
      document.title = `${sign}${mins}:${secs.toString().padStart(2, '0')} · ${activeTask.title} - PulseTask`;
    } else {
      document.title = 'PulseTask';
    }
  }, [activeTask]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      // View shortcuts
      if (e.key >= '1' && e.key <= '4' && !e.metaKey && !e.ctrlKey) {
        const modes = ['focus', 'list', 'stats', 'settings'] as const;
        setViewMode(modes[parseInt(e.key) - 1]);
        return;
      }
      
      // Overlay toggle
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        toggleOverlay();
        return;
      }
      
      // New task
      if (e.key.toLowerCase() === 'n' && !e.metaKey && !e.ctrlKey) {
        setViewMode('focus');
        return;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setViewMode, toggleOverlay]);
  
  const handleCreateTask = useCallback((title: string, duration: number, subtasks?: SubtaskWithTime[], autoStart: boolean = false) => {
    const id = addTask(title, duration, undefined, subtasks);
    if (autoStart) {
      startTask(id);
    }
    setViewMode('focus');
  }, [addTask, startTask, setViewMode]);
  
  const handleSelectTask = useCallback((task: typeof tasks[0]) => {
    if (task.status === 'completed' || task.status === 'expired' || task.status === 'archived') {
      // For completed/expired tasks, just view them without changing status
      viewTask(task.id);
      setViewMode('focus');
      return;
    }
    if (task.status === 'pending') {
      // View pending task but don't auto-start
      viewTask(task.id);
    } else if (task.status === 'paused') {
      // View paused task
      viewTask(task.id);
    } else if (task.status === 'running') {
      // View running task
      viewTask(task.id);
    }
    setViewMode('focus');
  }, [viewTask, setViewMode]);
  
  const renderMainContent = () => {
    switch (viewMode) {
      case 'focus':
        if (!activeTask || activeTask.status === 'completed' || activeTask.status === 'archived') {
          return <IdleState onCreateTask={handleCreateTask} />;
        }
        return (
          <FocusView
            task={activeTask}
            onStart={() => startTask(activeTask.id)}
            onPause={() => pauseTask(activeTask.id)}
            onResume={() => resumeTask(activeTask.id)}
            onComplete={() => completeTask(activeTask.id)}
            onReset={() => resetTask(activeTask.id)}
            onSnooze={(secs) => snoozeTask(activeTask.id, secs)}
            onCompleteSubtask={(subtaskId) => completeSubtask(activeTask.id, subtaskId)}
          />
        );
      
      case 'list':
        return (
          <TaskList
            tasks={tasks}
            activeTaskId={activeTaskId}
            onSelectTask={handleSelectTask}
            onCreateTask={handleCreateTask}
          />
        );
      
      case 'stats':
        return <StatsDashboard metrics={metrics} />;
      
      case 'settings':
        return <SettingsPanel />;
      
      default:
        return null;
    }
  };
  
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <AppHeader
        viewMode={viewMode}
        onViewChange={setViewMode}
        onToggleOverlay={toggleOverlay}
        isOverlayVisible={isOverlayVisible}
      />
      
      <main className="flex-1 overflow-auto">
        {renderMainContent()}
      </main>
      
      {/* Overlay */}
      {isOverlayVisible && (
        <div className="fixed bottom-6 right-6 z-50">
          <CompactOverlay
            task={activeTask}
            mode={overlayMode}
            onStart={() => activeTask && startTask(activeTask.id)}
            onPause={() => activeTask && pauseTask(activeTask.id)}
            onResume={() => activeTask && resumeTask(activeTask.id)}
            onComplete={() => activeTask && completeTask(activeTask.id)}
            onModeChange={setOverlayMode}
            onClose={toggleOverlay}
          />
        </div>
      )}
      
      {/* Status bar for running task indicator */}
      {activeTask && viewMode !== 'focus' && ['running', 'paused', 'expired'].includes(activeTask.status) && (
        <button
          onClick={() => setViewMode('focus')}
          className={cn(
            'fixed bottom-0 left-0 right-0 h-12 border-t',
            'flex items-center justify-between px-4',
            'bg-surface-1/95 backdrop-blur-sm',
            'hover:bg-surface-2 transition-colors',
            activeTask.status === 'expired' && 'border-expired/30 bg-expired/5'
          )}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              'w-2 h-2 rounded-full',
              activeTask.status === 'running' && 'bg-running animate-pulse',
              activeTask.status === 'paused' && 'bg-paused',
              activeTask.status === 'expired' && 'bg-expired animate-pulse'
            )} />
            <span className="text-sm font-medium truncate max-w-[200px]">
              {activeTask.title}
            </span>
          </div>
          <div className={cn(
            'font-mono text-sm font-medium',
            activeTask.status === 'expired' && 'text-expired'
          )}>
            {(() => {
              const remaining = activeTask.duration - activeTask.elapsed;
              const mins = Math.floor(Math.abs(remaining) / 60);
              const secs = Math.abs(remaining) % 60;
              const sign = remaining < 0 ? '-' : '';
              return `${sign}${mins}:${secs.toString().padStart(2, '0')}`;
            })()}
          </div>
        </button>
      )}
    </div>
  );
}
