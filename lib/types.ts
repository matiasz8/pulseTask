export type TaskStatus = 'pending' | 'running' | 'paused' | 'expired' | 'completed' | 'archived';

export interface Subtask {
  id: string;
  title: string;
  duration: number; // in seconds - individual duration for this subtask
  elapsed: number; // in seconds - elapsed time for this subtask
  completed: boolean;
  order: number;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  duration: number; // in seconds (sum of all subtask durations if subtasks exist)
  elapsed: number; // in seconds (total across all subtasks)
  status: TaskStatus;
  subtasks: Subtask[];
  currentSubtaskIndex: number;
  createdAt: Date;
  completedAt?: Date;
  expiredAt?: Date;
  pausedAt?: Date;
  overtime: number; // seconds past expiration
}

export interface TaskMetrics {
  completionRate: number;
  expirationRate: number;
  averageOvertime: number;
  pauseFragmentation: number;
  focusConsistency: number;
  totalTasksCompleted: number;
  totalTasksExpired: number;
  totalFocusTime: number;
}

export type ViewMode = 'focus' | 'list' | 'stats' | 'settings';

export type OverlayMode = 'normal' | 'compact' | 'ultracompact';

export interface AppState {
  tasks: Task[];
  activeTaskId: string | null;
  viewMode: ViewMode;
  overlayMode: OverlayMode;
  isOverlayVisible: boolean;
}
