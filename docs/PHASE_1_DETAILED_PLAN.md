# Phase 1 Implementation Plan: Focus Tab & Settings

**Branch**: `feature/v0.3.0-design-implementation`
**Effort**: 20-30 hours
**Duration**: 1-2 weeks
**Status**: IN PROGRESS

---

## Overview

Phase 1 delivers core UX improvements:
- Polish the Focus tab UI
- Implement complete Settings tab
- Add window title countdown

This gets 80% of the design vision with foundational work.

---

## Task Breakdown

### Task 1.1: Focus Tab UI Polish (2-4 hours)

**Current State**: Functional but basic
**Target**: Professional, polished appearance

#### What to Change

1. **Button Layout Improvement**
   - Current: Basic buttons in a row
   - Target: Better grouped buttons with visual hierarchy
   - Implementation:
     ```python
     # src/pulse_task/ui/group_window.py
     # In Focus tab init:
     
     # Quick presets group
     quick_presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
     for duration_str in ["5m", "15m", "25m", "45m", "60m"]:
         btn = Gtk.Button(label=duration_str)
         btn.connect("clicked", self._on_quick_duration, parse_duration(duration_str))
         quick_presets.append(btn)
     
     # Custom duration group
     custom_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
     custom_entry = Gtk.Entry()
     custom_entry.set_placeholder_text("Custom duration (e.g., 30m)")
     custom_btn = Gtk.Button(label="Set")
     custom_group.append(custom_entry)
     custom_group.append(custom_btn)
     ```

2. **Visual Feedback**
   - Add selected/active state
   - Use libadwaita accent colors
   - CSS classes: `.duration-button`, `.duration-button:checked`

3. **Keyboard Shortcuts**
   - Ctrl+1 = 5m
   - Ctrl+2 = 15m
   - Ctrl+3 = 25m
   - Ctrl+4 = 45m
   - Ctrl+5 = 60m
   - Ctrl+Return = Create task
   - Implementation:
     ```python
     self.connect("key-press-event", self._on_key_press)
     
     def _on_key_press(self, widget, event):
         if event.state & Gdk.ModifierType.CONTROL_MASK:
             if event.keyval == Gdk.KEY_1:
                 self._set_duration(5 * 60)
             # etc...
     ```

#### Files to Modify
- `src/pulse_task/ui/group_window.py` - Refine FocusTab class
- `src/pulse_task/ui/styles.css` - Add focus tab styles

#### Tests to Add
- test_focus_tab_buttons.py: Button click handlers
- test_focus_tab_shortcuts.py: Keyboard shortcuts
- 4-6 tests total

#### Acceptance Criteria
- ✅ Buttons visually grouped
- ✅ Keyboard shortcuts work (Ctrl+1-5)
- ✅ Visual feedback on button press
- ✅ Styling consistent with libadwaita

---

### Task 1.2: Settings Tab Implementation (12-16 hours)

**Current State**: GSettings schema exists, no UI
**Target**: Complete PreferencesWindow with 3 sections

#### Architecture

```
src/pulse_task/ui/settings_window.py
├── SettingsWindow (main window)
│   ├── GeneralPage
│   │   ├── DarkModeSwitch
│   │   └── WeekStartComboBox
│   ├── FocusPage
│   │   ├── AutoStartSwitch
│   │   ├── TitleCountdownSwitch
│   │   └── PauseOnBlurSwitch
│   └── NotificationsPage
│       ├── NotificationsSwitch
│       ├── WarningsSwitch
│       └── ThresholdSpinner
```

#### Implementation Details

**1.2.1 GeneralPage** (3-4 hours)
```python
# src/pulse_task/ui/settings_window.py

class GeneralPage(Adw.PreferencesPage):
    def __init__(self):
        super().__init__()
        self.set_title("General")
        self.set_icon_name("emblem-system-symbolic")
        
        # Dark mode group
        dark_group = Adw.PreferencesGroup()
        dark_group.set_title("Appearance")
        
        dark_row = Adw.SwitchRow()
        dark_row.set_title("Dark mode")
        dark_row.set_subtitle("Use dark theme for reduced eye strain")
        dark_switch = dark_row.get_first_child()
        dark_switch.connect("notify::active", self._on_dark_mode_changed)
        
        self._bind_gsettings(dark_switch, "dark-mode")
        dark_group.add(dark_row)
        self.add(dark_group)
        
        # Calendar group
        calendar_group = Adw.PreferencesGroup()
        calendar_group.set_title("Calendar")
        
        week_row = Adw.ComboRow()
        week_row.set_title("Week starts on")
        week_row.set_model(Gtk.StringList.new(["Monday", "Sunday"]))
        self._bind_gsettings(week_row, "week-start")
        calendar_group.add(week_row)
        self.add(calendar_group)
    
    def _bind_gsettings(self, widget, key):
        # Helper to bind GTK4 widget to GSettings
        self.settings.bind(
            key, widget, 
            "active" if isinstance(widget, Gtk.Switch) else "selected",
            Gio.SettingsBindFlags.DEFAULT
        )
    
    def _on_dark_mode_changed(self, switch, param):
        # Apply theme immediately
        style_manager = Adw.StyleManager.get_default()
        if switch.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
```

**1.2.2 FocusPage** (4-5 hours)
```python
class FocusPage(Adw.PreferencesPage):
    def __init__(self):
        super().__init__()
        self.set_title("Focus")
        self.set_icon_name("focus-symbolic")
        
        group = Adw.PreferencesGroup()
        group.set_title("Focus Behavior")
        
        # Auto-start next task
        auto_start_row = Adw.SwitchRow()
        auto_start_row.set_title("Auto-start next task")
        auto_start_row.set_subtitle("Automatically begin the next pending task")
        self._bind_gsettings(auto_start_row, "auto-start-next")
        group.add(auto_start_row)
        
        # Show time in title
        title_row = Adw.SwitchRow()
        title_row.set_title("Show remaining time in title")
        title_row.set_subtitle("Display countdown in window title and taskbar")
        self._bind_gsettings(title_row, "show-time-in-title")
        group.add(title_row)
        
        # Pause on blur
        blur_row = Adw.SwitchRow()
        blur_row.set_title("Pause on window blur")
        blur_row.set_subtitle("Auto-pause when switching windows")
        self._bind_gsettings(blur_row, "pause-on-blur")
        group.add(blur_row)
        
        self.add(group)
```

**1.2.3 NotificationsPage** (4-5 hours)
```python
class NotificationsPage(Adw.PreferencesPage):
    def __init__(self):
        super().__init__()
        self.set_title("Notifications")
        self.set_icon_name("notifications-symbolic")
        
        group = Adw.PreferencesGroup()
        group.set_title("Desktop Notifications")
        
        # Enable notifications
        notify_row = Adw.SwitchRow()
        notify_row.set_title("Show desktop notifications")
        notify_row.set_subtitle("Send notifications for task events")
        self._bind_gsettings(notify_row, "notifications-enabled")
        group.add(notify_row)
        
        # Expiration warnings
        warning_row = Adw.SwitchRow()
        warning_row.set_title("Expiration warnings")
        warning_row.set_subtitle("Notify before task expires")
        self._bind_gsettings(warning_row, "expiration-warnings")
        group.add(warning_row)
        
        # Warning threshold
        threshold_row = Adw.SpinRow()
        threshold_row.set_title("Warning threshold")
        threshold_row.set_subtitle("Minutes before expiration to warn")
        threshold_adjustment = Gtk.Adjustment(
            value=5, lower=1, upper=60, step_increment=1
        )
        threshold_row.set_adjustment(threshold_adjustment)
        self._bind_gsettings(threshold_row, "warning-threshold")
        group.add(threshold_row)
        
        self.add(group)
```

#### Files to Create
- `src/pulse_task/ui/settings_window.py` (200-300 lines)
- `src/pulse_task/ui/styles_settings.css` (50-100 lines)

#### Files to Modify
- `src/pulse_task/ui/group_window.py` - Add Settings menu item
- `pyproject.toml` - Ensure Adw dependency (already there)

#### GSettings Schema Update
Already exists in `data/org.gnome.Pulse.gschema.xml`, verify keys:
- `dark-mode` (boolean)
- `week-start` (string: "Monday" or "Sunday")
- `auto-start-next` (boolean)
- `show-time-in-title` (boolean)
- `pause-on-blur` (boolean)
- `notifications-enabled` (boolean)
- `expiration-warnings` (boolean)
- `warning-threshold` (integer, 1-60)

#### Tests to Add
- `tests/test_settings_window.py` (8-12 tests)
  - Test each SwitchRow binding
  - Test GSettings persistence
  - Test immediate application

#### Acceptance Criteria
- ✅ Settings window opens from main menu
- ✅ All 8 preferences have UI controls
- ✅ Changes persist to GSettings
- ✅ Changes apply immediately
- ✅ Accessible keyboard navigation
- ✅ Responsive layout

---

### Task 1.3: Window Title Countdown (4-6 hours)

**Current State**: Not implemented
**Target**: "15m 30s - PulseTask" in window title

#### Implementation

```python
# In src/pulse_task/ui/group_window.py

class GroupExecutionWindow(Gtk.ApplicationWindow):
    def __init__(self, ...):
        # ... existing code ...
        
        # Add title update to timer loop
        GLib.timeout_add(100, self._update_title)  # 100ms timer already exists
        
        self.show_title_countdown = True  # controlled by settings
    
    def _update_title(self):
        if not self.show_title_countdown:
            self.set_title("PulseTask")
            return True
        
        if not self.service or not self.service.active_group:
            self.set_title("PulseTask")
            return True
        
        group = self.service.active_group
        remaining = group.remaining_time_seconds()
        
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            title = f"{minutes:02d}m {seconds:02d}s - PulseTask"
        else:
            title = "PulseTask"
        
        self.set_title(title)
        return True  # Continue timer
    
    def _on_settings_changed(self, settings, key):
        if key == "show-time-in-title":
            self.show_title_countdown = settings.get_boolean(key)
            if not self.show_title_countdown:
                self.set_title("PulseTask")
```

#### Files to Modify
- `src/pulse_task/ui/group_window.py` - Add _update_title method
- Connect to GSettings "show-time-in-title" change signal

#### Tests to Add
- `tests/test_window_title.py` (4-6 tests)
  - Test title format
  - Test countdown update frequency
  - Test setting disables feature

#### Acceptance Criteria
- ✅ Title updates every second when task active
- ✅ Format: "MM:SS - PulseTask"
- ✅ Resets to "PulseTask" when no task
- ✅ Can be disabled via settings
- ✅ Works on both X11 and Wayland

---

## Implementation Order

1. **Task 1.1**: Focus Tab Polish (start here - quick win)
2. **Task 1.3**: Window Title Countdown (simple, no dependencies)
3. **Task 1.2**: Settings Tab (most complex, depends on 1.1 being done)

This order ensures quick wins first, then tackle complexity.

---

## Testing Strategy

### Unit Tests
```python
# tests/test_focus_tab.py
def test_quick_button_sets_duration():
    tab = FocusTab()
    btn = tab.find_button("15m")
    btn.emit("clicked")
    assert tab.get_duration() == 15 * 60

def test_keyboard_shortcut_ctrl_1():
    tab = FocusTab()
    tab.emit("key-press-event", mock_event(Gdk.KEY_1, Gdk.CONTROL_MASK))
    assert tab.get_duration() == 5 * 60
```

### Integration Tests
```python
# tests/test_settings_integration.py
def test_settings_persist_to_gsettings():
    window = SettingsWindow()
    switch = window.get_dark_mode_switch()
    switch.set_active(True)
    
    settings = Gio.Settings.new("org.gnome.Pulse")
    assert settings.get_boolean("dark-mode") == True

def test_title_countdown_respects_setting():
    settings = Gio.Settings.new("org.gnome.Pulse")
    settings.set_boolean("show-time-in-title", False)
    
    window = GroupExecutionWindow(...)
    assert window.get_title() == "PulseTask"  # not "15m 30s - ..."
```

### Manual Testing
- [ ] Buttons visually grouped and respond to clicks
- [ ] Keyboard shortcuts work smoothly
- [ ] Settings window opens and closes
- [ ] All controls respond to clicks
- [ ] Settings persist across app restarts
- [ ] Title updates smoothly every second
- [ ] Dark mode toggle applies immediately
- [ ] Test on both X11 and Wayland

---

## Code Quality Checklist

- [ ] All code follows existing style (ruff compliant)
- [ ] All functions type-hinted (mypy compliant)
- [ ] All public functions documented
- [ ] No new dependencies added
- [ ] Tests added for all new functionality
- [ ] 85%+ coverage maintained
- [ ] No performance regressions

---

## Git Commit Strategy

```
commit 1: "feat: Polish Focus tab UI and add keyboard shortcuts"
commit 2: "feat: Implement Settings window with preferences"
commit 3: "feat: Add window title countdown display"
commit 4: "test: Add comprehensive Phase 1 tests"
commit 5: "docs: Update CHANGELOG for v0.3.0-alpha1"
```

All commits to `feature/v0.3.0-design-implementation` branch.

---

## Success Criteria

Phase 1 is complete when:
- ✅ Focus tab is polished (2 hours + review)
- ✅ Settings tab is fully functional (6 hours + review)
- ✅ Window title countdown works (1 hour + review)
- ✅ All tests pass (>85% coverage)
- ✅ No lint/typecheck errors
- ✅ Keyboard accessible
- ✅ Ready for Phase 2

---

## Next: Phase 2

Once Phase 1 completes:
- Stats dashboard visualization
- Metric cards with trends
- Daily/weekly/monthly selector
- Simple charts

Estimated: 1-2 weeks

---

*Ready to implement. Waiting for codebase analysis.*
