'use client';

import { cn } from '@/lib/utils';
import { ViewMode } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Kbd } from '@/components/ui/kbd';
import { 
  Focus,
  List,
  BarChart3,
  Settings,
  Layers
} from 'lucide-react';

interface AppHeaderProps {
  viewMode: ViewMode;
  onViewChange: (mode: ViewMode) => void;
  onToggleOverlay: () => void;
  isOverlayVisible: boolean;
  className?: string;
}

const navItems: { mode: ViewMode; label: string; icon: typeof Focus; shortcut: string }[] = [
  { mode: 'focus', label: 'Focus', icon: Focus, shortcut: '1' },
  { mode: 'list', label: 'Tasks', icon: List, shortcut: '2' },
  { mode: 'stats', label: 'Stats', icon: BarChart3, shortcut: '3' },
  { mode: 'settings', label: 'Settings', icon: Settings, shortcut: '4' },
];

export function AppHeader({ 
  viewMode, 
  onViewChange, 
  onToggleOverlay,
  isOverlayVisible,
  className 
}: AppHeaderProps) {
  return (
    <header className={cn(
      'h-14 border-b border-border bg-surface-1/80 backdrop-blur-sm',
      'flex items-center justify-between px-4',
      className
    )}>
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">P</span>
        </div>
        <span className="font-semibold text-lg tracking-tight">PulseTask</span>
      </div>
      
      {/* Navigation */}
      <nav className="flex items-center gap-1">
        {navItems.map(({ mode, label, icon: Icon, shortcut }) => (
          <button
            key={mode}
            onClick={() => onViewChange(mode)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              viewMode === mode 
                ? 'bg-accent text-accent-foreground' 
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{label}</span>
            <Kbd className="hidden md:inline text-[10px] opacity-50">{shortcut}</Kbd>
          </button>
        ))}
      </nav>
      
      {/* Actions */}
      <div className="flex items-center gap-2">
        <Button
          variant={isOverlayVisible ? 'secondary' : 'ghost'}
          size="sm"
          onClick={onToggleOverlay}
          className="gap-2"
        >
          <Layers className="w-4 h-4" />
          <span className="hidden sm:inline">Overlay</span>
          <Kbd className="hidden md:inline text-[10px]">⌘O</Kbd>
        </Button>
      </div>
    </header>
  );
}
