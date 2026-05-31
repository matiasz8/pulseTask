# FASE 1 Sprint 1: Overlay Mode & Group Execution UI

## Objective

Build the visual foundation for group task execution with an elegant, non-intrusive overlay mode that maintains the "calm execution environment" philosophy.

## Features

### 1.1 - Group Execution Window (Main Component)

A dedicated window for executing task groups with:

- **Timer Display** (dominant)
  - Large, readable countdown showing remaining time in group
  - Format: MM:SS with clear contrast
  - Updates every 100ms for smooth animation

- **Task Queue**
  - List of tasks in execution order
  - Current task highlighted
  - Completed/skipped tasks shown with check marks
  - Progress bar showing overall group progress (%)

- **Control Panel**
  - Play/Pause button
  - Skip current task button
  - Stop group button
  - Quick-add task to group (optional, V2)

- **Stats Footer**
  - Tasks completed / Total tasks
  - Current task name and remaining time for it
  - Elapsed time in group

### 1.2 - Overlay Mode (Minimal Non-Intrusive)

Compact floating window (320x120px):

- Small timer (18pt font, high contrast)
- Current task name (14pt)
- Minimal buttons: Pause, Skip
- Keyboard shortcut: Ctrl+Alt+T to toggle
- Always-on-top, semi-transparent when unfocused
- Mouse over to show full opacity

### 1.3 - Preferences Integration

Add to Preferences window:

- [ ] Enable overlay mode toggle
- [ ] Overlay opacity slider (0.3 - 1.0)
- [ ] Overlay size preset (small/medium/large)
- [ ] Keyboard shortcut configuration
- [ ] Auto-hide on task completion
- [ ] Sound notifications on task transitions

### 1.4 - Design System Updates

Create cohesive visual language:

- **Color Palette**
  - Primary: #0a1419 (GNOME dark)
  - Accent: #1d9ef6 (GNOME blue)
  - Success: #33d17a (GNOME green)
  - Alert: #f66151 (GNOME red)
  - Neutral: #f6f5f4 (GNOME light)

- **Typography**
  - Headings: 18pt (Source Sans Pro bold)
  - Body: 13pt (Source Sans Pro regular)
  - Mono: 11pt (JetBrains Mono for timer)

- **Spacing**
  - Baseline: 8px grid
  - Padding: 16px (window), 8px (components)
  - Border radius: 6px (soft corners)
  - Shadows: Subtle elevation (0px 2px 4px rgba(0,0,0,0.1))

- **Animation**
  - Transition: 200ms ease-out (default)
  - Timer tick: 100ms smooth updates
  - Button hover: 100ms scale + shadow

## Technical Implementation

### File Structure

```
src/pulse_task/ui/
├── group_window.py          # Main GroupExecutionWindow
├── group_overlay.py         # Overlay mode widget
├── group_components.py      # Reusable components (TimerDisplay, TaskQueue)
└── styles_group.css         # Group-specific CSS

docs/
├── FASE1_SPRINT1_SPEC.md    # This file
└── DESIGN_TOKENS.md         # Design system reference
```

### Core Classes

**GroupExecutionWindow**
- Inherits: Adw.ApplicationWindow
- Shows full group execution interface
- Manages GroupService lifecycle (start, pause, resume, complete)
- Updates timer every 100ms via GLib.timeout_add

**GroupOverlay**
- Inherits: Gtk.Window (with type=popup for always-on-top)
- Compact timer + task name display
- 320x120px with minimal controls
- Transparency managed by opacity property

**TimerDisplay**
- Inherits: Gtk.Label
- Formats time as MM:SS
- Applied CSS classes for styling
- Mono font for readability

**TaskQueue**
- Inherits: Gtk.Box (vertical)
- List of task rows (current highlighted)
- Progress bar above list
- Custom CSS for task row styling

### Integration with GroupService

```python
class GroupExecutionWindow:
    def __init__(self, group_id: str, service: GroupService):
        self.service = service
        self.group = service.get_group(group_id)
        self.timer_handle = None
        self._setup_ui()
        self._start_timer()
    
    def _start_timer(self) -> None:
        """Start timer update loop."""
        def update_timer():
            # Update GroupService state
            # Refresh UI
            # Check for completion
            return True  # Keep timer running
        
        self.timer_handle = GLib.timeout_add(100, update_timer)
    
    def pause_group(self) -> None:
        """Pause execution."""
        self.service.pause_group(self.group.id)
        GLib.source_remove(self.timer_handle)
    
    def resume_group(self) -> None:
        """Resume execution."""
        self.service.resume_group(self.group.id)
        self._start_timer()
```

### CSS Structure

**styles_group.css**

```css
/* Group Execution Window */
.group-window {
    background-color: @theme_base_color;
    color: @theme_fg_color;
}

.timer-display {
    font-family: "JetBrains Mono";
    font-size: 64pt;
    font-weight: bold;
    color: @theme_accent_color;
    margin: 32px;
}

.task-queue {
    background-color: @theme_bg_color;
    border-radius: 6px;
    padding: 8px;
}

.task-row {
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 4px;
}

.task-row.current {
    background-color: @theme_accent_color;
    color: white;
    font-weight: bold;
}

.task-row.completed::before {
    content: "✓";
    margin-right: 8px;
    color: @theme_success_color;
}

/* Overlay */
.group-overlay {
    background-color: rgba(10, 20, 25, 0.95);
    border: 1px solid rgba(29, 158, 246, 0.3);
    border-radius: 8px;
    padding: 12px;
}

.overlay-timer {
    font-family: "JetBrains Mono";
    font-size: 28pt;
    color: @theme_accent_color;
}

.overlay-task {
    font-size: 11pt;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 4px;
}
```

## Acceptance Criteria

- [ ] GroupExecutionWindow fully functional (start/pause/resume/complete)
- [ ] Timer updates smoothly (100ms refresh rate)
- [ ] Overlay mode togglable with Ctrl+Alt+T
- [ ] Task queue shows current task + progress
- [ ] All UI elements respond to theme changes (dark/light)
- [ ] Keyboard navigation works (Tab between buttons)
- [ ] Screen reader announces task transitions
- [ ] CSS integrates with existing styles
- [ ] No performance regression (FPS stable)
- [ ] Screenshot tests pass for all states

## Timeline

- **Design & Mockups**: 2 hours
- **GroupExecutionWindow implementation**: 6 hours
- **Overlay mode**: 4 hours
- **CSS & Styling**: 3 hours
- **Testing & QA**: 4 hours
- **Documentation**: 1 hour

**Total: ~20 hours** (~2-3 days for full-time dev)

## Dependencies

- FASE 0.1 (GroupService) ✅
- GTK4 + libadwaita
- GLib event loop for timer

## Known Limitations / Future Enhancements

- No drag-and-drop reordering of tasks in queue (V2)
- No task detail view in overlay (by design - minimal)
- No nested group support (V2)
- Notifications will be basic (no D-Bus actions in V1)

