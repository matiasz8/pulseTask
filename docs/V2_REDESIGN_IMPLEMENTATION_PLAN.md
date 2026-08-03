# PulseTask V2 Redesign Implementation Plan

**Date:** 2024-12-21
**Branch:** `feature/v2-redesign`
**Target:** GTK4 + libadwaita (Python)

---

## 📋 Executive Summary

This plan adapts the React/Next.js V2 design (from `pulse-task-v2-design.zip`) into GTK4+libadwaita, maintaining the modular architecture while delivering a modern, focus-first user experience.

---

## 🎯 V2 Design Goals

| Goal | Description |
|------|-------------|
| **Focus-First UX** | One primary action per state, minimal noise |
| **Always-Visible Overlay** | Compact timer window for multitasking |
| **Visual Hierarchy** | Strong countdown prominence |
| **Keyboard-First** | Full keyboard navigation for all flows |
| **Native GNOME** | libadwaita conventions, Wayland/X11 safe |

---

## 🏗️ Architecture Mapping

### React Components → GTK4 Widgets

| React Component | GTK4 Implementation | Location |
|----------------|---------------------|----------|
| `PulseTaskApp` | `MainWindow` (Adw.ApplicationWindow) | `ui/main_window.py` |
| `FocusView` | `FocusView` (Adw.ToolbarView) | `ui/focus_view.py` |
| `CompactOverlay` | `CompactOverlay` (Gtk.Window) | `ui/compact_overlay.py` |
| `TaskList` | `TaskList` (Gtk.ListBox) | `ui/task_list.py` |
| `StatsDashboard` | `StatsDashboard` (Adw.NavigationPage) | `ui/stats_view.py` |
| `SettingsPanel` | `SettingsWindow` (Adw.PreferencesWindow) | `ui/settings_window.py` |
| `CountdownDisplay` | `CountdownWidget` (Gtk.DrawingArea) | `ui/countdown_widget.py` |
| `TaskCard` | `TaskCard` (Gtk.ListBoxRow) | `ui/task_card.py` |
| `AppHeader` | `Adw.HeaderBar` | Built-in |

### Design Tokens → CSS Variables

| Token | CSS Variable | Default |
|-------|--------------|---------|
| Background | `@background_color` | `@window_bg_color` |
| Running | `@running_color` | `#2ec27e` |
| Paused | `@paused_color` | `#e5a11c` |
| Expired | `@expired_color` | `#e01b24` |
| Completed | `@completed_color` | `#33d17a` |
| Primary | `@accent_color` | `@accent_bg_color` |

---

## 📁 File Structure

```
src/pulse_task/ui/
├── __init__.py
├── main_window.py          # Main application window (refactored)
├── focus_view.py           # NEW: Focus mode view
├── compact_overlay.py      # NEW: Always-on-top overlay
├── task_list.py            # NEW: Task list view
├── task_card.py            # NEW: Individual task card
├── stats_view.py           # NEW: Statistics dashboard
├── settings_window.py      # Refactored settings
├── countdown_widget.py     # NEW: Custom countdown display
├── status_bar.py           # NEW: Bottom status bar
├── a11y.py                 # Accessibility helpers
├── desktop.py              # Desktop integration helpers
├── assets/
│   └── *.svg
└── styles/
    ├── base.css            # Base theme tokens
    ├── main.css            # Main window styles
    ├── focus.css           # Focus view styles
    ├── overlay.css         # Overlay styles
    └── components.css      # Reusable component styles
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Days 1-3)
**Goal:** Restructure UI module, create base components

#### Tasks:
1. [ ] Create new file structure
2. [ ] Extract CSS to separate files
3. [ ] Create `CountdownWidget` custom widget
4. [ ] Create base `TaskCard` component
5. [ ] Refactor `MainWindow` to use new structure

#### Deliverables:
- New file structure created
- Countdown widget with visual states
- CSS architecture established

---

### Phase 2: Focus View (Days 4-6)
**Goal:** Implement focus-first main view

#### Tasks:
1. [ ] Create `FocusView` widget
2. [ ] Implement task title + description display
3. [ ] Integrate `CountdownWidget` (size="xl")
4. [ ] Add subtask progress list
5. [ ] Implement state-based controls:
   - [ ] Pending → Start button
   - [ ] Running → Pause + Complete
   - [ ] Paused → Resume + Reset
   - [ ] Expired → Complete + Reset + Snooze
   - [ ] Completed → Reset
6. [ ] Add keyboard shortcuts (Space, Enter, etc.)

#### Visual States:
```
┌─────────────────────────────────────────────┐
│                  FOCUS VIEW                 │
├─────────────────────────────────────────────┤
│                                             │
│              Task Title Here                │
│        Optional description text            │
│                                             │
│         ┌─────────────────────┐             │
│         │     12:34 / 25:00   │             │
│         │   ████████░░░░░░░   │             │
│         └─────────────────────┘             │
│                                             │
│    Steps Progress                2/4        │
│    ┌────────────────────────────────┐       │
│    │ ✓ Step 1 (completed)          │       │
│    │ → Step 2 (current)            │       │
│    │   Step 3 (future)             │       │
│    │   Step 4 (future)             │       │
│    └────────────────────────────────┘       │
│                                             │
│    [ ▶ Start ]  [ Space ]                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

### Phase 3: Compact Overlay (Days 7-9)
**Goal:** Implement always-on-top overlay with 3 density modes

#### Tasks:
1. [ ] Create `CompactOverlay` as `Gtk.Window`
2. [ ] Set window type to `POPUP` with `always-on-top`
3. [ ] Implement 3 modes:
   - [ ] Normal (320px) - Full info
   - [ ] Compact (288px) - Title + timer + controls
   - [ ] Ultra-compact (auto) - Timer + play/pause only
4. [ ] Add mode switcher buttons
5. [ ] Implement drag-to-move
6. [ ] Add keyboard toggle (Ctrl+O)
7. [ ] Remember last position

#### Overlay Modes:
```
NORMAL (320px)          COMPACT (288px)        ULTRA-COMPACT
┌──────────────────┐    ┌────────────────┐    ┌──────────┐
│ Task Title    [X]│    │ Title    [_][X]│    │ 12:34 [▶]│
│ Description      │    │                │    │     [+]  │
│                  │    │  12:34 / 25:00 │    └──────────┘
│  12:34 / 25:00   │    │  ████████░░░░  │
│  ████████░░░░░░  │    │                │
│                  │    │ [Pause] [Done] │
│ Step 2/4         │    └────────────────┘
│                  │
│ [Pause] [Done]   │
└──────────────────┘
```

---

### Phase 4: Task List View (Days 10-11)
**Goal:** Implement task list with inline actions

#### Tasks:
1. [ ] Create `TaskList` view
2. [ ] Implement grouped display (active/archived)
3. [ ] Add task selection → focus view
4. [ ] Create quick-add task dialog
5. [ ] Add inline action buttons (start, edit, archive)
6. [ ] Implement keyboard navigation

---

### Phase 5: Stats Dashboard (Days 12-13)
**Goal:** Implement statistics visualization

#### Tasks:
1. [ ] Create `StatsDashboard` view
2. [ ] Display time range selector (Today/7d/30d)
3. [ ] Show core metrics:
   - [ ] Completion rate
   - [ ] Expiration rate
   - [ ] Resume-after-pause rate
4. [ ] Add simple trend visualization (using Gtk.DrawingArea)
5. [ ] Display activity summary

#### Metrics Layout:
```
┌─────────────────────────────────────────────┐
│            STATISTICS DASHBOARD             │
├─────────────────────────────────────────────┤
│  [ Today ] [ 7 Days ] [ 30 Days ]          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  Completed   │  │  Expired    │          │
│  │     12       │  │      3      │          │
│  │   (80%)      │  │   (20%)     │          │
│  └─────────────┘  └─────────────┘          │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  Resumed     │  │  Snoozed    │          │
│  │      5       │  │      2      │          │
│  │   (25%)      │  │   (10%)     │          │
│  └─────────────┘  └─────────────┘          │
│                                             │
│  ─────────────────────────────────────────  │
│  Weekly Trend                               │
│  ┌────────────────────────────────────┐     │
│  │      ╭─╮         ╭─╮              │     │
│  │   ╭─╯  ╰─╮   ╭─╯  ╰─╮   ╭─╮     │     │
│  │──╯        ╰─╯        ╰─╯   ╰─────│     │
│  │ Mon Tue Wed Thu Fri Sat Sun       │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

---

### Phase 6: Status Bar (Day 14)
**Goal:** Implement bottom status bar for background tasks

#### Tasks:
1. [ ] Create `StatusBar` widget
2. [ ] Show when task running and not in focus view
3. [ ] Display: status dot + title + countdown
4. [ ] Click → return to focus view
5. [ ] Visual states for running/paused/expired

---

### Phase 7: Keyboard Shortcuts (Day 15)
**Goal:** Complete keyboard navigation

#### Shortcuts Map:
| Shortcut | Action |
|----------|--------|
| `Space` | Start/Pause/Resume active task |
| `Enter` | Complete task or current subtask |
| `Ctrl+N` | New task |
| `Ctrl+O` | Toggle overlay |
| `Ctrl+R` or `Cmd+R` | Reset task |
| `1-4` | Switch views (Focus/List/Stats/Settings) |
| `Escape` | Close overlay/dialog |
| `↑/↓` | Navigate task list |
| `Tab` | Cycle through controls |

---

### Phase 8: Settings Integration (Day 16)
**Goal:** Refactor settings to match V2 design

#### Tasks:
1. [ ] Convert to `Adw.PreferencesWindow`
2. [ ] Add sections:
   - [ ] General (default duration, close behavior)
   - [ ] Appearance (theme, archive visibility)
   - [ ] Alerts (sounds, notifications)
   - [ ] Overlay (default mode, always on top)
   - [ ] Keyboard (shortcuts reference)

---

### Phase 9: CSS Polish (Days 17-18)
**Goal:** Visual refinement and theming

#### Tasks:
1. [ ] Implement light/dark theme support
2. [ ] Add CSS transitions for state changes
3. [ ] Refine countdown animation
4. [ ] Polish overlay blur effect
5. [ ] Test with system theme colors
6. [ ] Ensure high contrast accessibility

---

### Phase 10: Testing & QA (Days 19-20)
**Goal:** Ensure quality and accessibility

#### Tasks:
1. [ ] Add unit tests for new components
2. [ ] Test keyboard navigation
3. [ ] Test screen reader (Orca)
4. [ ] Test Wayland and X11
5. [ ] Test overlay positioning
6. [ ] Performance profiling
7. [ ] Update documentation

---

## 🔧 Technical Implementation Notes

### Countdown Widget Implementation

```python
class CountdownWidget(Gtk.DrawingArea):
    """Custom countdown display with visual states."""
    
    def __init__(self):
        super().__init__()
        self.set_size_request(200, 120)
        self.set_draw_func(self._draw)
        
        # State
        self.elapsed = 0
        self.duration = 0
        self.status = "pending"
        self.size = "lg"  # sm, md, lg, xl
        
    def _draw(self, area, cr, width, height):
        # Draw progress arc
        # Draw time text
        # Draw status indicator
        pass
```

### Overlay Window Implementation

```python
class CompactOverlay(Gtk.Window):
    """Always-on-top compact overlay window."""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(320, -1)
        
        # Enable dragging
        self._drag_controller = Gtk.GestureDrag()
        self._drag_controller.connect("drag-update", self._on_drag_update)
        self.add_controller(self._drag_controller)
        
        # Mode: normal, compact, ultracompact
        self.mode = "normal"
```

### Theme Integration

```css
/* styles/base.css */

/* Running state */
@define-color running_color #2ec27e;
@define-color running_bg alpha(@running_color, 0.1);

/* Paused state */
@define-color paused_color #e5a11c;
@define-color paused_bg alpha(@paused_color, 0.1);

/* Expired state */
@define-color expired_color #e01b24;
@define-color expired_bg alpha(@expired_color, 0.1);

/* Completed state */
@define-color completed_color #33d17a;
@define-color completed_bg alpha(@completed_color, 0.1);

/* Countdown styles */
.countdown-xl {
    font-size: 48px;
    font-weight: 700;
    font-family: monospace;
}

.countdown-lg {
    font-size: 36px;
    font-weight: 600;
    font-family: monospace;
}

.countdown-md {
    font-size: 24px;
    font-weight: 600;
    font-family: monospace;
}

.countdown-sm {
    font-size: 14px;
    font-weight: 500;
    font-family: monospace;
}

/* Overlay styles */
.overlay {
    background: alpha(@window_bg_color, 0.95);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    border: 1px solid alpha(@borders, 0.5);
    box-shadow: 0 8px 32px alpha(black, 0.2);
}

/* Focus view */
.focus-view {
    padding: 48px;
}

.focus-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Task card states */
.task-card-running {
    border-left: 3px solid @running_color;
    background: @running_bg;
}

.task-card-paused {
    border-left: 3px solid @paused_color;
    background: @paused_bg;
}

.task-card-expired {
    border-left: 3px solid @expired_color;
    background: @expired_bg;
}
```

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Keyboard-only completion rate | 100% of primary flows |
| Time to start task (keyboard) | < 2 seconds |
| Overlay toggle time | < 500ms |
| Screen reader compatibility | Full Orca support |
| Wayland/X11 compatibility | 100% feature parity |
| Test coverage | > 85% |

---

## 🔗 References

- **V2 Design Source:** `pulse-task-v2-design.zip`
- **V2 PRD:** `docs/DESIGN_PRD_V2.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Existing POCs:** `docs/pocs/`

---

## ✅ Definition of Done

- [ ] All phases completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Accessibility verified
- [ ] Wayland/X11 tested
- [ ] PR approved and merged

---

**Status:** 🟡 In Progress
**Next Action:** Begin Phase 1 - Foundation
</contents>