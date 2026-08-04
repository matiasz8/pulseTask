'use client';

import { cn } from '@/lib/utils';
import { Task } from '@/lib/types';
import { TaskCard } from './task-card';
import { TaskCreator } from './task-creator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';

interface TaskListProps {
  tasks: Task[];
  activeTaskId: string | null;
  onSelectTask: (task: Task) => void;
  onCreateTask: (title: string, duration: number, subtasks?: SubtaskWithTime[], autoStart?: boolean) => void;
  className?: string;
}

type FilterType = 'active' | 'completed' | 'all';

interface SubtaskWithTime {
  title: string;
  duration: number;
}

export function TaskList({ 
  tasks, 
  activeTaskId, 
  onSelectTask, 
  onCreateTask,
  className 
}: TaskListProps) {
  const [filter, setFilter] = useState<FilterType>('active');
  
  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') {
      return !['completed', 'archived'].includes(task.status);
    }
    if (filter === 'completed') {
      return task.status === 'completed';
    }
    return task.status !== 'archived';
  });
  
  const activeTasks = tasks.filter(t => !['completed', 'archived'].includes(t.status));
  const completedTasks = tasks.filter(t => t.status === 'completed');
  
  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h2 className="text-lg font-semibold mb-3">Tasks</h2>
        <Tabs value={filter} onValueChange={(v) => setFilter(v as FilterType)}>
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="active" className="text-xs">
              Active ({activeTasks.length})
            </TabsTrigger>
            <TabsTrigger value="completed" className="text-xs">
              Done ({completedTasks.length})
            </TabsTrigger>
            <TabsTrigger value="all" className="text-xs">
              All
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      
      <ScrollArea className="flex-1 px-4">
        <div className="py-4 space-y-3">
          {filter === 'active' && (
            <TaskCreator onCreateTask={onCreateTask} />
          )}
          
          {filteredTasks.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p className="text-sm">
                {filter === 'active' && 'No active tasks'}
                {filter === 'completed' && 'No completed tasks yet'}
                {filter === 'all' && 'No tasks yet'}
              </p>
            </div>
          ) : (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                isActive={task.id === activeTaskId}
                onClick={() => onSelectTask(task)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
