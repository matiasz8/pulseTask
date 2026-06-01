# Phase 3: System Integration - Detailed Implementation Plan

**Scope:** GNOME deep integration (D-Bus, Quick Settings, notifications, search provider, shortcuts)
**Timeline:** 1-2 weeks (reduced scope: focus on notifications + Quick Settings first)
**Target:** v0.3.0-beta readiness

## Phase 3 Subtasks

### 3.1 Desktop Notifications (Priority: HIGH)
**Duration:** 4-6 hours
**Status:** Completed

#### What to Build
Actionable D-Bus notifications for key PulseTask events.

#### Notification Scenarios

1. **Task Expiration**
   - Title: "Task expired"
   - Body: "[Task name]"
   - Actions:
     - "Snooze 5m" → Extend task by 5 minutes
     - "Start next" → Skip to next task
     - "Dismiss" → Close notification
   - Urgency: Normal
   - Timeout: 10 seconds (persistent on screen)

2. **Time Warning (5 min before expiration)**
   - Title: "5 minutes remaining"
   - Body: "[Task name]"
   - Actions:
     - "Extend 5m" → Add 5 more minutes
     - "Continue" → Dismiss notification
   - Urgency: Critical
   - Timeout: 5 seconds

3. **Focus Lost (Optional)**
   - Title: "Window focus lost"
   - Body: "Auto-paused due to window blur"
   - Actions:
     - "Resume" → Resume task
     - "Keep paused" → Remain paused
   - Urgency: Low
   - Timeout: 3 seconds

#### Implementation

**File:** `src/pulse_task/system/notifications.py` (NEW)

```python
class NotificationManager:
    """D-Bus notification manager for PulseTask."""
    
    def send_task_expired(self, task_name: str) -> None:
        """Send task expiration notification with actions."""
        # Use org.freedesktop.Notifications D-Bus interface
        # Implementation: Send dbus message to notification daemon
        
    def send_time_warning(self, task_name: str, minutes_remaining: int) -> None:
        """Send time warning notification."""
        # Urgent priority, action buttons
        
    def send_focus_lost(self) -> None:
        """Send focus loss notification."""
        # Low priority, informational
```

**Integration Points:**
- Hook into `GroupService.update_group_elapsed_time()` (check time remaining)
- Hook into `GroupService.skip_task_in_group()` (task expiration detected)
- Hook into `GroupExecutionWindow` (focus-out-event handler)

**Tests:**
- Unit tests for notification formatting
- Mock D-Bus calls
- Test action button handlers
- Test notification timeout behavior

### 3.2 Quick Settings Widget (Priority: MEDIUM)
**Duration:** 4-6 hours
**Status:** Pending

#### What to Build
GNOME Quick Settings toggle for pause/resume.

#### Requirements
- Show current group execution status
- Toggle pause/resume from Quick Settings
- Show remaining time
- Update in real-time

#### Implementation

**File:** `src/pulse_task/system/quick_settings.py` (NEW)

```python
class QuickSettingsWidget:
    """GNOME Quick Settings widget for PulseTask."""
    
    def __init__(self, service: GroupService):
        # Create Adw.ActionRow or similar
        # Bind to current group status
        # Set up pause/resume action
        
    def update_status(self, is_paused: bool, time_remaining: int):
        """Update widget display on status change."""
```

**Implementation Approach:**
- Use GSettings for state
- Use D-Bus signals for real-time updates
- Leverage libadwaita for UI consistency

**Tests:**
- Unit tests for status updates
- Integration tests with GroupService
- Mock D-Bus signal emissions

### 3.3 Global Keyboard Shortcuts (Priority: MEDIUM)
**Duration:** 2-3 hours
**Status:** Pending

#### What to Build
System-level keyboard shortcuts (via Settings daemon).

#### Shortcuts to Implement
- `Super+Alt+P` - Pause/Resume current task
- `Super+Alt+N` - Start new task (if none active)
- `Super+Alt+S` - Show statistics window
- `Super+Alt+T` - Bring window to foreground

#### Implementation

**File:** `src/pulse_task/system/shortcuts.py` (NEW)

```python
class GlobalShortcuts:
    """Global keyboard shortcuts for PulseTask."""
    
    def register_shortcuts(self) -> None:
        """Register global shortcuts via Settings daemon."""
        # Use org.gnome.Shell.Extensions interface
        # Or use custom keybindings in GSettings
        
    def handle_shortcut(self, shortcut_id: str) -> None:
        """Handle global shortcut activation."""
```

**GSettings Schema Extension:**
```xml
<key name="global-shortcuts" type="a{ss}">
    <default>{
        'pause-resume': '&lt;Super&gt;alt+p',
        'new-task': '&lt;Super&gt;alt+n',
        'show-stats': '&lt;Super&gt;alt+s'
    }</default>
</key>
```

**Tests:**
- Unit tests for shortcut parsing
- Integration tests with Settings daemon
- Mock D-Bus calls

### 3.4 Search Provider Integration (Priority: LOW)
**Duration:** 3-4 hours
**Status:** Pending

#### What to Build
GNOME search integration (Activities search).

#### Functionality
- Search for tasks in search bar
- Show active group execution status
- Jump to app on selection
- Show recent completions

#### Implementation

**File:** `src/pulse_task/system/search_provider.py` (NEW)

```python
class SearchProvider:
    """GNOME search provider for PulseTask."""
    
    def provide_search_results(self, search_terms: str) -> list[dict]:
        """Provide search results for Activities search."""
        # Query GroupService for matching tasks
        # Return formatted results
        
    def activate_result(self, result_id: str) -> None:
        """Activate search result."""
        # Bring app to foreground
        # Navigate to task
```

**D-Bus Interface:**
```
org.gnome.Shell.SearchProvider2
  GetInitialResultSet(as terms) → au
  GetSubsystemQuery(as terms) → (as)
  GetResultMetas(au result_ids) → aa{sv}
  ActivateResult(u result_id, as terms, u timestamp) → void
  SetActive(b active) → void
```

**Tests:**
- Unit tests for search result formatting
- Integration tests with shell
- Mock D-Bus search interface

### 3.5 D-Bus Service Complete Implementation (Priority: MEDIUM)
**Duration:** 4-5 hours
**Status:** Pending

#### Current State
`src/pulse_task/dbus/service.py` exists but is stubbed.

#### What to Implement
- Full D-Bus service registration
- Method exposure for:
  - `pause_group(group_id)` → void
  - `resume_group(group_id)` → void
  - `get_current_group()` → (ss) [id, name]
  - `get_group_stats()` → a{sv}
- Signal emission for:
  - `GroupStatusChanged(s group_id, s status)`
  - `TimeRemaining(s group_id, i seconds)`
  - `TaskCompleted(s group_id, s task_id)`

#### Implementation

**File:** `src/pulse_task/dbus/service.py` (EXPAND)

```python
class DBusService:
    """Full D-Bus service implementation."""
    
    def register(self) -> bool:
        """Register D-Bus service on session bus."""
        # Use dbus-python or GLib.dbus bindings
        # Register org.gnome.Pulse service
        # Export methods and signals
        
    @dbus.method('org.gnome.Pulse', in_signature='s', out_signature='')
    def pause_group(self, group_id: str) -> None:
        """Pause a group (D-Bus method)."""
        self.service.pause_group_execution(group_id)
        self.emit_signal('GroupStatusChanged', group_id, 'PAUSED')
```

**Tests:**
- D-Bus client tests (using gdbus)
- Method call and response validation
- Signal emission verification
- Service registration/unregistration

## Implementation Order

1. **Week 1:**
   - 3.1 Desktop Notifications (4-6h)
   - 3.2 Quick Settings (4-6h)
   - 3.3 Global Shortcuts (2-3h)

2. **Week 2:**
   - 3.4 Search Provider (3-4h)
   - 3.5 D-Bus Full Implementation (4-5h)
   - Integration testing & refinement

## Success Criteria

- [x] All notifications display correctly
- [x] Action buttons work (snooze, extend, dismiss)
- [ ] Quick Settings widget shows status in real-time
- [ ] Global shortcuts registered and functional
- [ ] Search provider returns results in Activities
- [ ] D-Bus service fully registered
- [ ] All tests passing (154+ base)
- [ ] 100% lint compliance
- [ ] 100% type checking
- [ ] Zero regressions

## Dependencies

**External:**
- `dbus-python` (D-Bus bindings)
- `pydbus` (alternative D-Bus library)
- System: D-Bus session bus, GNOME Shell, systemd (for user services)

**Internal:**
- GroupService (already exists)
- GSettings integration (Phase 1)
- Notification system (system/notify.py exists)

## Testing Strategy

**Unit Tests:**
- Notification formatting and edge cases
- Shortcut parsing and validation
- Search result generation

**Integration Tests:**
- D-Bus method calls and responses
- Service registration
- Real-time updates via signals

**System Tests:**
- Notification appearance in GNOME
- Quick Settings visibility
- Shortcut activation

**Manual Testing:**
- Create task group and trigger expiration (test notification)
- Click notification action buttons
- Toggle pause from Quick Settings
- Test global shortcuts
- Search in Activities

## Estimated Total Time

- Notifications: 4-6 hours
- Quick Settings: 4-6 hours
- Global Shortcuts: 2-3 hours
- Search Provider: 3-4 hours
- D-Bus Full: 4-5 hours
- Testing & QA: 3-4 hours
- **Total: 20-28 hours** (1-2 weeks full-time)

## Risk Assessment

- **LOW:** Notification system (mature, well-documented)
- **MEDIUM:** D-Bus service (requires careful registration)
- **MEDIUM:** Quick Settings (depends on GNOME version)
- **MEDIUM:** Global shortcuts (requires Settings daemon integration)
- **HIGH:** Search provider (Shell integration complex)

## Rollback Plan

Each component can be independently disabled:
- Notifications: Graceful degradation (no notifications)
- Quick Settings: Works without (in-app only)
- Global Shortcuts: Optional, fallback to manual
- Search Provider: Optional feature
- D-Bus Service: Full fallback to local-only mode

---

**Next Step:** Start with 3.1 (Desktop Notifications) using agent implementation
