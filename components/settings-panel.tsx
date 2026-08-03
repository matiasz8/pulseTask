'use client';

import { cn } from '@/lib/utils';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { 
  Settings, 
  Bell, 
  Eye,
  Keyboard,
  Monitor,
  Volume2
} from 'lucide-react';

interface SettingsPanelProps {
  className?: string;
}

interface SettingGroupProps {
  title: string;
  icon: typeof Settings;
  children: React.ReactNode;
}

function SettingGroup({ title, icon: Icon, children }: SettingGroupProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Icon className="w-4 h-4" />
        {title}
      </div>
      <div className="space-y-4 pl-6">
        {children}
      </div>
    </div>
  );
}

interface SettingRowProps {
  label: string;
  description?: string;
  children: React.ReactNode;
}

function SettingRow({ label, description, children }: SettingRowProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="space-y-0.5">
        <Label className="text-sm font-medium">{label}</Label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      {children}
    </div>
  );
}

export function SettingsPanel({ className }: SettingsPanelProps) {
  return (
    <div className={cn('p-6 max-w-2xl mx-auto', className)}>
      <div className="mb-8">
        <h2 className="text-xl font-semibold">Settings</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configure PulseTask to match your workflow
        </p>
      </div>
      
      <div className="space-y-8">
        {/* General */}
        <SettingGroup title="General" icon={Settings}>
          <SettingRow
            label="Dark mode"
            description="Use dark theme for reduced eye strain"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Start week on Monday"
            description="For weekly metrics calculations"
          >
            <Switch defaultChecked />
          </SettingRow>
        </SettingGroup>
        
        <Separator />
        
        {/* Focus */}
        <SettingGroup title="Focus" icon={Eye}>
          <SettingRow
            label="Auto-start next task"
            description="Automatically begin the next pending task"
          >
            <Switch />
          </SettingRow>
          
          <SettingRow
            label="Show remaining time in title"
            description="Display countdown in browser tab"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Pause on window blur"
            description="Auto-pause when switching windows"
          >
            <Switch />
          </SettingRow>
        </SettingGroup>
        
        <Separator />
        
        {/* Notifications */}
        <SettingGroup title="Notifications" icon={Bell}>
          <SettingRow
            label="Desktop notifications"
            description="Show system notifications for task events"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Expiration warnings"
            description="Notify before task expires"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Warning threshold"
            description="Minutes before expiration to warn"
          >
            <span className="text-sm font-mono text-muted-foreground">5 min</span>
          </SettingRow>
        </SettingGroup>
        
        <Separator />
        
        {/* Sound */}
        <SettingGroup title="Sound" icon={Volume2}>
          <SettingRow
            label="Sound effects"
            description="Play sounds for task events"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Tick sound"
            description="Subtle ticking during countdown"
          >
            <Switch />
          </SettingRow>
        </SettingGroup>
        
        <Separator />
        
        {/* Overlay */}
        <SettingGroup title="Overlay" icon={Monitor}>
          <SettingRow
            label="Remember overlay position"
            description="Keep overlay in last used position"
          >
            <Switch defaultChecked />
          </SettingRow>
          
          <SettingRow
            label="Show on all workspaces"
            description="Overlay visible across virtual desktops"
          >
            <Switch defaultChecked />
          </SettingRow>
        </SettingGroup>
        
        <Separator />
        
        {/* Keyboard Shortcuts */}
        <SettingGroup title="Keyboard Shortcuts" icon={Keyboard}>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Start/Pause timer</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">Space</kbd>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Complete task/subtask</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">Enter</kbd>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">New task</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">N</kbd>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Reset task</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">⌘R</kbd>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Toggle overlay</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">⌘O</kbd>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Open settings</span>
              <kbd className="px-2 py-1 rounded bg-muted font-mono text-xs">⌘,</kbd>
            </div>
          </div>
        </SettingGroup>
      </div>
    </div>
  );
}
