'use client';

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Kbd } from '@/components/ui/kbd';
import { Plus, Clock, List } from 'lucide-react';

interface SubtaskWithTime {
  title: string;
  duration: number; // in minutes
}

interface TaskCreatorProps {
  onCreateTask: (title: string, duration: number, subtasks?: SubtaskWithTime[]) => void;
  className?: string;
}

const QUICK_DURATIONS = [
  { label: '5m', seconds: 5 * 60 },
  { label: '15m', seconds: 15 * 60 },
  { label: '25m', seconds: 25 * 60 },
  { label: '45m', seconds: 45 * 60 },
  { label: '60m', seconds: 60 * 60 },
];

export function TaskCreator({ onCreateTask, className }: TaskCreatorProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [title, setTitle] = useState('');
  const [customMinutes, setCustomMinutes] = useState('');
  const [selectedDuration, setSelectedDuration] = useState<number | null>(null);
  const [subtasks, setSubtasks] = useState<SubtaskWithTime[]>([]);
  const [showSubtasks, setShowSubtasks] = useState(false);
  const [subtaskTitle, setSubtaskTitle] = useState('');
  const [subtaskDuration, setSubtaskDuration] = useState('');
  
  const handleCreate = useCallback(() => {
    if (!title.trim()) return;
    
    let totalDuration = selectedDuration;
    if (!totalDuration && customMinutes) {
      const mins = parseInt(customMinutes, 10);
      if (!isNaN(mins) && mins > 0) {
        totalDuration = mins * 60;
      }
    }
    
    // If there are subtasks, calculate total duration from them
    if (subtasks.length > 0) {
      totalDuration = subtasks.reduce((sum, st) => sum + (st.duration * 60), 0);
    }
    
    if (!totalDuration) return;
    
    onCreateTask(
      title.trim(), 
      totalDuration, 
      subtasks.length > 0 ? subtasks : undefined
    );
    
    // Reset form
    setTitle('');
    setCustomMinutes('');
    setSelectedDuration(null);
    setSubtasks([]);
    setSubtaskTitle('');
    setSubtaskDuration('');
    setShowSubtasks(false);
    setIsExpanded(false);
  }, [title, selectedDuration, customMinutes, subtasks, onCreateTask]);
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleCreate();
    }
    if (e.key === 'Escape') {
      setIsExpanded(false);
    }
  }, [handleCreate]);
  
  const addSubtask = useCallback(() => {
    if (subtaskTitle.trim() && subtaskDuration) {
      const mins = parseInt(subtaskDuration, 10);
      if (!isNaN(mins) && mins > 0) {
        setSubtasks(prev => [...prev, { title: subtaskTitle.trim(), duration: mins }]);
        setSubtaskTitle('');
        setSubtaskDuration('');
      }
    }
  }, [subtaskTitle, subtaskDuration]);
  
  const removeSubtask = useCallback((index: number) => {
    setSubtasks(prev => prev.filter((_, i) => i !== index));
  }, []);
  
  const totalSubtaskTime = subtasks.reduce((sum, st) => sum + st.duration, 0);
  
  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        className={cn(
          'w-full p-4 rounded-xl border border-dashed border-border/60',
          'bg-surface-1/50 hover:bg-surface-1 hover:border-border',
          'transition-all duration-200 group',
          'flex items-center justify-center gap-3 text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          className
        )}
      >
        <Plus className="w-5 h-5 group-hover:text-foreground transition-colors" />
        <span className="text-sm font-medium group-hover:text-foreground transition-colors">
          New Task
        </span>
        <Kbd className="ml-2 opacity-60">N</Kbd>
      </button>
    );
  }
  
  return (
    <div 
      className={cn(
        'rounded-xl border border-border bg-card p-5 space-y-5',
        'shadow-sm',
        className
      )}
      onKeyDown={handleKeyDown}
    >
      <div className="space-y-3">
        <Input
          autoFocus
          placeholder="Task title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="text-lg font-medium bg-transparent border-none px-0 h-auto focus-visible:ring-0 placeholder:text-muted-foreground/50"
        />
      </div>
      
      {/* Duration Selection */}
      {subtasks.length === 0 && (
        <div className="space-y-3">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            Duration
          </label>
          <div className="flex flex-wrap gap-2">
            {QUICK_DURATIONS.map(({ label, seconds }) => (
              <button
                key={seconds}
                onClick={() => {
                  setSelectedDuration(seconds);
                  setCustomMinutes('');
                }}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  'border',
                  selectedDuration === seconds
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-secondary/50 text-secondary-foreground border-border hover:bg-secondary'
                )}
              >
                {label}
              </button>
            ))}
            <div className="flex items-center gap-2">
              <Input
                type="number"
                placeholder="mins"
                value={customMinutes}
                onChange={(e) => {
                  setCustomMinutes(e.target.value);
                  setSelectedDuration(null);
                }}
                className="w-24 h-9 text-sm"
                min={1}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Subtasks */}
      <div className="space-y-3">
        <button
          onClick={() => setShowSubtasks(!showSubtasks)}
          className="text-xs font-medium text-muted-foreground flex items-center gap-2 hover:text-foreground transition-colors"
        >
          <List className="w-3.5 h-3.5" />
          Subtasks {subtasks.length > 0 && `(${subtasks.length} • ${totalSubtaskTime}m)`}
        </button>
        
        {showSubtasks && (
          <div className="space-y-3 pl-5 border-l border-border">
            {subtasks.map((subtask, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground font-medium">{index + 1}.</span>
                <div className="flex-1">
                  <div className="font-medium">{subtask.title}</div>
                  <div className="text-xs text-muted-foreground">{subtask.duration}m</div>
                </div>
                <button
                  onClick={() => removeSubtask(index)}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
            <div className="flex gap-2 pt-2">
              <Input
                placeholder="Subtask..."
                value={subtaskTitle}
                onChange={(e) => setSubtaskTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSubtask();
                  }
                }}
                className="flex-1 h-8 text-sm"
              />
              <Input
                type="number"
                placeholder="mins"
                value={subtaskDuration}
                onChange={(e) => setSubtaskDuration(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSubtask();
                  }
                }}
                className="w-20 h-8 text-sm"
                min={1}
              />
              <Button
                size="sm"
                variant="ghost"
                onClick={addSubtask}
                disabled={!subtaskTitle.trim() || !subtaskDuration}
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
      
      {/* Actions */}
      <div className="flex items-center justify-between pt-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(false)}
        >
          Cancel
        </Button>
        <div className="flex items-center gap-2">
          <Kbd className="text-xs">⌘ Enter</Kbd>
          <Button
            onClick={handleCreate}
            disabled={!title.trim() || (!selectedDuration && !customMinutes && subtasks.length === 0)}
            size="sm"
          >
            Create Task
          </Button>
        </div>
      </div>
    </div>
  );
}
