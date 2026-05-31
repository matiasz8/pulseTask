# FASE 3: Deep GNOME Integration

## Overview
Transform PulseTask from a "GTK4 app" into a true GNOME citizen through tight shell integration, system notifications, and accessibility features that feel native to the GNOME ecosystem.

## Phase 3.1: D-Bus Service & Quick Settings Integration (Sprint 1)

### Goal
Enable GNOME Quick Settings toggle to pause/resume the active group.

### Components

**1. D-Bus Service** (`src/pulse_task/dbus/service.py`)
```python
# org.gnome.Pulse.Service
# org.gnome.Pulse.Service.SetPaused(bool paused) -> void
# org.gnome.Pulse.Service.GetStatus() -> string (IDLE, EXECUTING, PAUSED, COMPLETED)
# org.gnome.Pulse.Service.CurrentTaskName() -> string
# org.gnome.Pulse.Service.TimeRemaining() -> int (seconds)
# Signals: status-changed, time-updated
```

**2. D-Bus XML Interface** (`data/org.gnome.Pulse.xml`)
```xml
<!DOCTYPE node PUBLIC "-//freedesktop//D-Bus//DTD D-BUS Service Interface 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/service-interface.dtd">
<node>
  <interface name="org.gnome.Pulse.Service">
    <property name="Status" type="s" access="read" />
    <property name="IsExecuting" type="b" access="read" />
    <property name="CurrentTaskName" type="s" access="read" />
    <property name="TimeRemaining" type="i" access="read" />
    <method name="SetPaused">
      <arg type="b" direction="in" name="paused" />
    </method>
    <method name="SkipCurrentTask" />
    <method name="StopExecution" />
    <signal name="StatusChanged">
      <arg type="s" name="status" />
    </signal>
    <signal name="TimeUpdated">
      <arg type="i" name="seconds_remaining" />
    </signal>
  </interface>
</node>
```

**3. GSettings Schema** (`data/org.gnome.Pulse.gschema.xml`)
```xml
<schemalist>
  <schema id="org.gnome.Pulse" path="/org/gnome/Pulse/" gettext-domain="pulsetask">
    <key type="b" name="show-overlay">
      <default>false</default>
      <summary>Show compact overlay window</summary>
    </key>
    <key type="i" name="overlay-opacity">
      <default>70</default>
      <summary>Overlay window opacity (0-100)</summary>
      <range min="0" max="100" />
    </key>
    <key type="s" name="last-group-id">
      <default>''</default>
      <summary>Last active group for quick resume</summary>
    </key>
  </schema>
</schemalist>
```

**4. Quick Settings Plugin** (`src/pulse_task/gnome/quick_settings.py`)
```python
# Register Quick Settings toggle in GNOME Shell
# Shows: "[ACTIVE TASK] 05:32"
# Click: Toggle pause
# Shift+Click: Open app

# Implementation: D-Bus signal → Shell redraws toggle
```

### Files to Create
- [ ] `src/pulse_task/dbus/service.py` - D-Bus service implementation
- [ ] `src/pulse_task/dbus/__init__.py` - D-Bus module
- [ ] `data/org.gnome.Pulse.xml` - D-Bus interface definition
- [ ] `data/org.gnome.Pulse.gschema.xml` - GSettings schema
- [ ] `src/pulse_task/gnome/quick_settings.py` - Quick Settings integration
- [ ] `tests/test_dbus_service.py` - D-Bus service tests

### Tests
- [ ] D-Bus methods return correct values
- [ ] Status property updates on group state change
- [ ] Time remaining decreases each second
- [ ] SetPaused(true) pauses group execution
- [ ] Signals emit on state changes

---

## Phase 3.2: Actionable Notifications (Sprint 2)

### Goal
Replace basic GTK4 notifications with full D-Bus notifications featuring action buttons.

### Components

**1. D-Bus Notifications** (`src/pulse_task/notifications/dbus_notify.py`)
```python
# org.freedesktop.Notifications
# Notify(app_name, replaces_id, icon, summary, body, actions, hints, timeout)

# Actions:
# - "pause" / "Pause" → Pause execution
# - "skip" / "Skip Task" → Skip current task
# - "stop" / "Stop" → End group execution
# - "open" / "Open App" → Bring app to foreground
```

**2. Notification Types**
- **Time Alert** (5 min remaining): "5 minutes left on [Group Name]"
  - Actions: Pause, Continue
- **Task Complete**: "[Task Name] finished in 12:34"
  - Actions: Next Task, Skip Remaining
- **Group Complete**: "[Group Name] finished! Stats: 3/4 tasks, 2 interruptions"
  - Actions: View Stats, Archive
- **Time Up**: "[Task Name] exceeded budget (was 5:00, now 5:45)"
  - Actions: Stop, Continue Anyway

**3. Notification Preferences**
- [ ] Disable notifications for "focus mode"
- [ ] Show/hide time alerts
- [ ] Show/hide task completions
- [ ] Persistent vs auto-close

### Files to Create
- [ ] `src/pulse_task/notifications/dbus_notify.py` - D-Bus notification implementation
- [ ] `src/pulse_task/notifications/__init__.py` - Notifications module
- [ ] `src/pulse_task/notifications/config.py` - Notification preferences
- [ ] `tests/test_notifications.py` - Notification tests

### Tests
- [ ] Notifications send via D-Bus
- [ ] Actions callback correctly
- [ ] Notifications respect preferences
- [ ] No duplicate notifications

---

## Phase 3.3: Search Provider Integration (Sprint 3)

### Goal
Enable searching tasks from GNOME Overview (Super key).

### Components

**1. Search Provider Plugin** (`src/pulse_task/gnome/search_provider.py`)
```python
# org.gnome.Shell.SearchProvider2
# GetInitialResultSet(terms) -> array of ids
# GetResultMetas(ids) -> array of metadata dicts
# ActivateResult(id, terms, timestamp)

# Search Results:
# "exec sprint" → Shows: "[EXECUTING] Sprint Focus (3/5 tasks, 12:34 remaining)"
# "stats daily" → Shows: "[STATS] Daily Report (completed: 8 tasks, interruptions: 2)"
```

**2. Search Result Types**
- Active/paused groups
- Completed groups
- Statistics views
- Quick actions: "Start new group", "View stats"

### Files to Create
- [ ] `src/pulse_task/gnome/search_provider.py` - Search integration
- [ ] `data/org.gnome.Pulse.SearchProvider.xml` - Search Provider D-Bus interface
- [ ] `tests/test_search_provider.py` - Search tests

### Tests
- [ ] Search returns correct task groups
- [ ] Result activation opens app + shows group
- [ ] Metadata formatting is correct

---

## Phase 3.4: Global Keyboard Shortcuts (Sprint 4)

### Goal
Register system-wide keyboard shortcuts without app being in focus.

### Components

**1. Global Shortcuts** (`src/pulse_task/gnome/global_shortcuts.py`)
```python
# Ctrl+Alt+T + P → Pause/Resume active group
# Ctrl+Alt+T + S → Skip current task
# Ctrl+Alt+T + O → Toggle overlay window
# Ctrl+Alt+T + N → Start new group (dialog)

# Implementation: gsettings keybindings + GNOME settings daemon
```

**2. Shortcut Registration**
```bash
# Register custom shortcuts
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybindings.custom0 name 'PulseTask Pause'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybindings.custom0 binding '<Primary><Alt>t p'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybindings.custom0 command 'dbus-send --session --type=method_call /org/gnome/Pulse/Service org.gnome.Pulse.Service.SetPaused boolean:true'
```

### Files to Create
- [ ] `src/pulse_task/gnome/global_shortcuts.py` - Global shortcuts setup
- [ ] `data/install-shortcuts.sh` - Installation script
- [ ] `tests/test_global_shortcuts.py` - Shortcut tests

### Tests
- [ ] Shortcuts register correctly
- [ ] Shortcuts trigger correct D-Bus methods
- [ ] Shortcuts work when app not focused

---

## Phase 3.5: Shell Integration (Sprint 5)

### Goal
Show active task in GNOME Shell top bar.

### Components

**1. Top Bar Integration**
```
[PulseTask icon] [Current Task] 05:32 (remaining)
```

**2. Implementation**
- D-Bus property updates Shell via signals
- Shell extension (optional, might be built-in GNOME 47+)
- Or: Use notification center for persistent display

### Files to Create
- [ ] `src/pulse_task/gnome/shell_extension/extension.js` (optional)
- [ ] `data/shell-extension.zip` (if needed)

---

## Implementation Strategy

### Timeline
- **3.1**: D-Bus + Quick Settings (1 week)
- **3.2**: Notifications (3 days)
- **3.3**: Search Provider (4 days)
- **3.4**: Global Shortcuts (3 days)
- **3.5**: Shell Integration (2 days)
- **Total**: ~3 weeks for full deep integration

### Testing Strategy
- Unit tests for each component
- Integration tests: D-Bus calls → GroupService updates
- Manual testing on GNOME 45+, 46, 47
- Accessibility testing: keyboard + D-Bus property inspection

### Documentation
- [ ] `docs/GNOME_INTEGRATION.md` - Technical guide
- [ ] `docs/GSETTINGS_SCHEMA.md` - Schema reference
- [ ] `docs/DBUS_API.md` - D-Bus methods + signals

---

## Success Criteria

✅ **Phase 3.1 Complete** when:
- [ ] D-Bus service responds to method calls
- [ ] Quick Settings toggle shows app status
- [ ] All tests pass

✅ **Phase 3.2 Complete** when:
- [ ] Notifications send via D-Bus
- [ ] Action buttons trigger correct callbacks
- [ ] Notifications respect user preferences

✅ **Phase 3.3 Complete** when:
- [ ] Search Provider returns results in Overview
- [ ] Result activation opens app correctly
- [ ] Performance acceptable (< 200ms search time)

✅ **Phase 3.4 Complete** when:
- [ ] Global shortcuts register
- [ ] Shortcuts work without app window
- [ ] User can customize shortcuts in GNOME Settings

✅ **Phase 3.5 Complete** when:
- [ ] Top bar shows active task (if shell extension)
- [ ] No visual conflicts with other extensions
- [ ] Works on Wayland + X11

---

## Known Challenges

1. **D-Bus Name Registration**
   - Solution: Use org.gnome.Pulse as service name (must be unique)

2. **Shell Extension Compatibility**
   - Solution: Test on GNOME 45, 46, 47, 48 (rolling updates)

3. **Notifications on Wayland**
   - Solution: Use D-Bus method calls (not XDG notifications which may have issues)

4. **Global Shortcuts on Wayland**
   - Solution: Use gnome-settings-daemon keybindings (standard GNOME approach)

5. **Permission Models**
   - Solution: User needs to grant permissions in GNOME Settings → Privacy (if applicable)

---

## Future Enhancements (v0.4+)

- [ ] Calendar integration (show active tasks in GNOME Calendar)
- [ ] Weather integration (show weather in overlay if breaks scheduled)
- [ ] Connectivity status (warn if going offline during important session)
- [ ] Custom themes via org.gnome.Pulse.CustomTheme
- [ ] Multi-user session sharing (read-only stats for team awareness)

---

## Rollback Plan

If FASE 3 causes issues:
- All D-Bus/GNOME features are optional (graceful degradation)
- If D-Bus unavailable, app still works as standalone GTK4 app
- Uninstall extensions: `gnome-extensions uninstall pulsetask@gnome.org`
- Reset settings: `dconf reset -f /org/gnome/Pulse/`
