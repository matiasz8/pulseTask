'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Task, TaskStatus, Subtask, TaskMetrics, ViewMode, OverlayMode } from './types';

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

interface SubtaskWithTime {
  title: string;
  duration: number; // in minutes
}

interface TaskStore {
  tasks: Task[];
  activeTaskId: string | null;
  viewMode: ViewMode;
  overlayMode: OverlayMode;
  isOverlayVisible: boolean;
  
  // Task actions
  addTask: (title: string, duration: number, description?: string, subtasks?: SubtaskWithTime[]) => string;
  updateTask: (id: string, updates: Partial<Task>) => void;
  deleteTask: (id: string) => void;
  
  // Execution actions
  startTask: (id: string) => void;
  pauseTask: (id: string) => void;
  resumeTask: (id: string) => void;
  completeTask: (id: string) => void;
  expireTask: (id: string) => void;
  resetTask: (id: string) => void;
  snoozeTask: (id: string, additionalTime: number) => void;
  archiveTask: (id: string) => void;
  
  // Timer actions
  tick: () => void;
  
  // Subtask actions
  addSubtask: (taskId: string, title: string) => void;
  completeSubtask: (taskId: string, subtaskId: string) => void;
  removeSubtask: (taskId: string, subtaskId: string) => void;
  
  // View actions
  setViewMode: (mode: ViewMode) => void;
  setOverlayMode: (mode: OverlayMode) => void;
  toggleOverlay: () => void;
  
  // Computed
  getActiveTask: () => Task | null;
  getMetrics: () => TaskMetrics;
}

export const useTaskStore = create<TaskStore>()(
  persist(
    (set, get) => ({
      tasks: [],
      activeTaskId: null,
      viewMode: 'focus',
      overlayMode: 'normal',
      isOverlayVisible: false,
      
      addTask: (title, duration, description, subtaskItems) => {
        const id = generateId();
        let subtasks: Subtask[] = [];
        let totalDuration = duration;
        
        if (subtaskItems && subtaskItems.length > 0) {
          subtasks = subtaskItems.map((st, i) => ({
            id: generateId(),
            title: st.title,
            duration: st.duration * 60, // convert minutes to seconds
            elapsed: 0,
            completed: false,
            order: i
          }));
          // Total duration is sum of all subtask durations
          totalDuration = subtasks.reduce((sum, s) => sum + s.duration, 0);
        }
        
        const task: Task = {
          id,
          title,
          description,
          duration: totalDuration,
          elapsed: 0,
          status: 'pending',
          subtasks,
          currentSubtaskIndex: 0,
          createdAt: new Date(),
          overtime: 0
        };
        
        set(state => ({ tasks: [...state.tasks, task] }));
        return id;
      },
      
      updateTask: (id, updates) => {
        set(state => ({
          tasks: state.tasks.map(t => t.id === id ? { ...t, ...updates } : t)
        }));
      },
      
      deleteTask: (id) => {
        set(state => ({
          tasks: state.tasks.filter(t => t.id !== id),
          activeTaskId: state.activeTaskId === id ? null : state.activeTaskId
        }));
      },
      
      startTask: (id) => {
        const { activeTaskId } = get();
        if (activeTaskId && activeTaskId !== id) {
          get().pauseTask(activeTaskId);
        }
        
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'running' as TaskStatus } : t
          ),
          activeTaskId: id
        }));
      },
      
      pauseTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'paused' as TaskStatus, pausedAt: new Date() } : t
          )
        }));
      },
      
      resumeTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'running' as TaskStatus, pausedAt: undefined } : t
          )
        }));
      },
      
      completeTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'completed' as TaskStatus, completedAt: new Date() } : t
          ),
          activeTaskId: state.activeTaskId === id ? null : state.activeTaskId
        }));
      },
      
      expireTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'expired' as TaskStatus, expiredAt: new Date() } : t
          )
        }));
      },
      
      resetTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { 
              ...t, 
              status: 'pending' as TaskStatus, 
              elapsed: 0, 
              overtime: 0,
              completedAt: undefined,
              expiredAt: undefined,
              pausedAt: undefined,
              currentSubtaskIndex: 0,
              subtasks: t.subtasks.map(s => ({ ...s, completed: false, elapsed: 0 }))
            } : t
          ),
          activeTaskId: state.activeTaskId === id ? null : state.activeTaskId
        }));
      },
      
      snoozeTask: (id, additionalTime) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { 
              ...t, 
              duration: t.duration + additionalTime,
              status: t.status === 'expired' ? 'running' as TaskStatus : t.status,
              expiredAt: undefined
            } : t
          )
        }));
      },
      
      archiveTask: (id) => {
        set(state => ({
          tasks: state.tasks.map(t => 
            t.id === id ? { ...t, status: 'archived' as TaskStatus } : t
          ),
          activeTaskId: state.activeTaskId === id ? null : state.activeTaskId
        }));
      },
      
      tick: () => {
        const { activeTaskId } = get();
        if (!activeTaskId) return;
        
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.id !== activeTaskId || t.status !== 'running') return t;
            
            // Handle subtask timing logic
            if (t.subtasks.length > 0) {
              const currentSubtask = t.subtasks[t.currentSubtaskIndex];
              if (!currentSubtask) {
                // All subtasks completed
                return {
                  ...t,
                  elapsed: t.duration,
                  status: 'expired' as TaskStatus,
                  expiredAt: new Date()
                };
              }
              
              // Increment elapsed on current subtask
              const newSubtasks = t.subtasks.map((s, idx) => {
                if (idx === t.currentSubtaskIndex) {
                  return { ...s, elapsed: s.elapsed + 1 };
                }
                return s;
              });
              
              // Check if current subtask is complete
              const subtaskElapsed = newSubtasks[t.currentSubtaskIndex].elapsed;
              const subtaskDuration = newSubtasks[t.currentSubtaskIndex].duration;
              let nextIndex = t.currentSubtaskIndex;
              
              if (subtaskElapsed >= subtaskDuration) {
                // Mark current subtask as completed
                newSubtasks[t.currentSubtaskIndex].completed = true;
                // Move to next subtask
                nextIndex = t.currentSubtaskIndex + 1;
              }
              
              const totalElapsed = newSubtasks.reduce((sum, s) => sum + s.elapsed, 0);
              const isExpired = totalElapsed >= t.duration;
              
              return {
                ...t,
                elapsed: totalElapsed,
                subtasks: newSubtasks,
                currentSubtaskIndex: nextIndex,
                overtime: isExpired ? totalElapsed - t.duration : 0,
                status: isExpired ? 'expired' as TaskStatus : t.status,
                expiredAt: isExpired && !t.expiredAt ? new Date() : t.expiredAt
              };
            }
            
            // No subtasks: simple timer logic
            const newElapsed = t.elapsed + 1;
            const isExpired = newElapsed >= t.duration;
            
            return {
              ...t,
              elapsed: newElapsed,
              overtime: isExpired ? newElapsed - t.duration : 0,
              status: isExpired && t.status !== 'expired' ? 'expired' as TaskStatus : t.status,
              expiredAt: isExpired && !t.expiredAt ? new Date() : t.expiredAt
            };
          })
        }));
      },
      
      addSubtask: (taskId, title) => {
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.id !== taskId) return t;
            return {
              ...t,
              subtasks: [...t.subtasks, {
                id: generateId(),
                title,
                completed: false,
                order: t.subtasks.length
              }]
            };
          })
        }));
      },
      
      completeSubtask: (taskId, subtaskId) => {
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.id !== taskId) return t;
            const newSubtasks = t.subtasks.map(s => 
              s.id === subtaskId ? { ...s, completed: true } : s
            );
            const completedIndex = newSubtasks.findIndex(s => s.id === subtaskId);
            return {
              ...t,
              subtasks: newSubtasks,
              currentSubtaskIndex: Math.max(t.currentSubtaskIndex, completedIndex + 1)
            };
          })
        }));
      },
      
      removeSubtask: (taskId, subtaskId) => {
        set(state => ({
          tasks: state.tasks.map(t => {
            if (t.id !== taskId) return t;
            return {
              ...t,
              subtasks: t.subtasks.filter(s => s.id !== subtaskId)
            };
          })
        }));
      },
      
      setViewMode: (mode) => set({ viewMode: mode }),
      setOverlayMode: (mode) => set({ overlayMode: mode }),
      toggleOverlay: () => set(state => ({ isOverlayVisible: !state.isOverlayVisible })),
      
      getActiveTask: () => {
        const { tasks, activeTaskId } = get();
        return tasks.find(t => t.id === activeTaskId) || null;
      },
      
      getMetrics: () => {
        const { tasks } = get();
        const completedTasks = tasks.filter(t => t.status === 'completed');
        const expiredTasks = tasks.filter(t => t.status === 'expired');
        const allFinished = [...completedTasks, ...expiredTasks];
        
        const totalTasks = allFinished.length || 1;
        const completionRate = completedTasks.length / totalTasks;
        const expirationRate = expiredTasks.length / totalTasks;
        const averageOvertime = expiredTasks.reduce((acc, t) => acc + t.overtime, 0) / (expiredTasks.length || 1);
        
        const tasksWithPauses = tasks.filter(t => t.pausedAt);
        const pauseFragmentation = tasksWithPauses.length / totalTasks;
        
        const focusConsistency = completionRate * (1 - pauseFragmentation);
        const totalFocusTime = tasks.reduce((acc, t) => acc + t.elapsed, 0);
        
        return {
          completionRate,
          expirationRate,
          averageOvertime,
          pauseFragmentation,
          focusConsistency,
          totalTasksCompleted: completedTasks.length,
          totalTasksExpired: expiredTasks.length,
          totalFocusTime
        };
      }
    }),
    {
      name: 'pulsetask-storage',
      partialize: (state) => ({
        tasks: state.tasks,
        overlayMode: state.overlayMode
      })
    }
  )
);
