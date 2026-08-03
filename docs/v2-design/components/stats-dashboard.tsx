'use client';

import { cn } from '@/lib/utils';
import { TaskMetrics } from '@/lib/types';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Pause,
  Target,
  Timer
} from 'lucide-react';

interface StatsDashboardProps {
  metrics: TaskMetrics;
  className?: string;
}

function formatTime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  const hours = Math.floor(seconds / 3600);
  const mins = Math.round((seconds % 3600) / 60);
  return `${hours}h ${mins}m`;
}

function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

interface MetricCardProps {
  label: string;
  value: string;
  description?: string;
  icon: typeof Clock;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

function MetricCard({ label, value, description, icon: Icon, trend, className }: MetricCardProps) {
  return (
    <div className={cn(
      'p-5 rounded-xl bg-card border border-border',
      className
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className={cn(
          'w-10 h-10 rounded-lg flex items-center justify-center',
          'bg-muted'
        )}>
          <Icon className="w-5 h-5 text-muted-foreground" />
        </div>
        {trend && trend !== 'neutral' && (
          <div className={cn(
            'flex items-center gap-1 text-xs font-medium',
            trend === 'up' ? 'text-completed' : 'text-expired'
          )}>
            {trend === 'up' ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold font-mono">{value}</p>
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}

export function StatsDashboard({ metrics, className }: StatsDashboardProps) {
  return (
    <div className={cn('p-6', className)}>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Operational Metrics</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Focus performance and execution patterns
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          label="Completion Rate"
          value={formatPercent(metrics.completionRate)}
          description="Tasks finished within allocated time"
          icon={Target}
          trend={metrics.completionRate >= 0.7 ? 'up' : 'down'}
        />
        
        <MetricCard
          label="Expiration Rate"
          value={formatPercent(metrics.expirationRate)}
          description="Tasks that exceeded time limit"
          icon={Timer}
          trend={metrics.expirationRate <= 0.3 ? 'up' : 'down'}
        />
        
        <MetricCard
          label="Average Overtime"
          value={formatTime(metrics.averageOvertime)}
          description="Time spent past expiration"
          icon={Clock}
          trend={metrics.averageOvertime <= 300 ? 'up' : 'down'}
        />
        
        <MetricCard
          label="Pause Fragmentation"
          value={formatPercent(metrics.pauseFragmentation)}
          description="Tasks interrupted by pauses"
          icon={Pause}
          trend={metrics.pauseFragmentation <= 0.2 ? 'up' : 'down'}
        />
        
        <MetricCard
          label="Focus Consistency"
          value={formatPercent(metrics.focusConsistency)}
          description="Completion × uninterrupted focus"
          icon={Target}
          trend={metrics.focusConsistency >= 0.6 ? 'up' : 'down'}
        />
        
        <MetricCard
          label="Total Focus Time"
          value={formatTime(metrics.totalFocusTime)}
          description={`${metrics.totalTasksCompleted} tasks completed`}
          icon={Clock}
        />
      </div>
      
      {/* Summary */}
      <div className="mt-8 p-5 rounded-xl bg-muted/50 border border-border">
        <h3 className="font-medium mb-2">Summary</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {metrics.totalTasksCompleted === 0 && metrics.totalTasksExpired === 0 ? (
            'Start completing tasks to see your operational metrics.'
          ) : metrics.focusConsistency >= 0.7 ? (
            'Excellent focus discipline. Your completion rate and uninterrupted execution are strong.'
          ) : metrics.focusConsistency >= 0.4 ? (
            'Moderate focus performance. Consider reducing pauses and improving time estimates.'
          ) : (
            'Focus needs improvement. Try shorter task durations and minimize interruptions.'
          )}
        </p>
      </div>
    </div>
  );
}
