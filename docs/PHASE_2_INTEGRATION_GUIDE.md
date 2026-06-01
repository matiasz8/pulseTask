# Phase 2 Integration Guide - Stats Dashboard

**Status:** Waiting for agent completion

## Expected Deliverables (From Agent)

The `phase-2-stats-dashboard` agent will create/modify:

### New Files
- `src/pulse_task/ui/stats_window.py` - Main stats window component (300-400 lines)
- `src/pulse_task/ui/styles_stats.css` - Stats-specific styling (150-200 lines)
- `tests/test_stats_window.py` - Stats window tests (50-100 lines)

### Modified Files
- `src/pulse_task/ui/__init__.py` - Export StatsWindow
- `src/pulse_task/ui/group_window.py` - (optional) Add stats access button

## Integration Steps (After Agent Completes)

### Step 1: Verify Agent Output
```bash
cd /home/nquiroga/Documents/personal/pulseTask

# Check git status
git status

# Verify all tests pass
make lint        # Must pass
make typecheck   # Must pass
make test        # Must pass (151+ tests)
```

### Step 2: Review Code Quality
- [ ] Check imports are correct
- [ ] Verify CSS loading mechanism
- [ ] Confirm GSettings integration (if used)
- [ ] Verify metric calculations
- [ ] Check period selector implementation

### Step 3: Add to Git
```bash
# Stage Phase 2 files
git add src/pulse_task/ui/stats_window.py
git add src/pulse_task/ui/styles_stats.css
git add src/pulse_task/ui/__init__.py
git add tests/test_stats_window.py

# Create commit
git commit -m "feat: Phase 2 - Stats dashboard with 6 metrics

Comprehensive statistics visualization:

Features:
- 6 metrics: Completion Rate, Expiration Rate, Overtime, Pause Fragmentation, Focus Consistency, Total Focus Time
- Period selector: Today, This Week, This Month
- Color-coded metric cards (green/yellow/red)
- Simple charts/heatmap visualization

Implementation:
- StatsWindow component with responsive layout
- Metric calculation integration with GroupStatsService
- CSS styling for metric cards
- Full keyboard navigation support

All tests passing: 151+ tests
Lint: ✅ Typecheck: ✅

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# Push to branch
git push origin feature/v0.3.0-design-implementation
```

### Step 4: Integration with Main UI (Optional for v0.3.0-alpha)

**Option A: Menu Access**
- Add "Statistics" menu item to GroupExecutionWindow header menu
- Click opens StatsWindow

**Option B: Keyboard Shortcut**
- Add Ctrl+S or Ctrl+T shortcut to open StatsWindow

**Option C: Dedicated Tab**
- Add stats tab to main interface (requires larger refactoring)

### Step 5: Manual Testing

```bash
# Run app
make run

# Test sequence:
# 1. Create and execute a group task
# 2. Open Statistics (from menu/shortcut)
# 3. Verify all 6 metrics display
# 4. Test period selector (Today/Week/Month)
# 5. Check color indicators (green/yellow/red)
# 6. Verify keyboard navigation (Tab, Arrow keys)
# 7. Check responsive layout at 800x600 minimum
```

### Step 6: Performance Check

```bash
# Verify memory usage doesn't spike
# Verify stats calculations complete < 100ms
# Verify UI remains responsive while calculating
```

## Phase 2 Expected Metrics Display

### Metric Cards (Example)

```
┌─ Completion Rate ─────────┐
│ 85%                       │
│ 17 of 20 tasks completed  │
│ ↑ +5% vs last week        │
└───────────────────────────┘

┌─ Expiration Rate ─────────┐
│ 10%                       │
│ 2 of 20 tasks expired     │
│ ↓ -3% vs last week        │
└───────────────────────────┘
```

### Period Selector

Radio buttons or segmented buttons:
- [ ] Today
- [x] This Week (default)
- [ ] This Month

### Color Indicators

- **Green** - Good performance (>80% completion, >50% focus)
- **Yellow** - Average performance (50-80%)
- **Red** - Poor performance (<50%)

## Known Implementation Patterns

The agent will likely use these patterns from Phase 1:

1. **GTK4 Window Setup**
   ```python
   class StatsWindow(Gtk.ApplicationWindow):
       def __init__(self, app, stats_service):
           super().__init__(application=app)
           # Build UI with Gtk.Box, Gtk.Label, etc.
   ```

2. **CSS Loading**
   ```python
   provider = Gtk.CssProvider()
   provider.load_from_path(str(css_path))
   Gtk.StyleContext.add_provider_for_display(display, provider, priority)
   ```

3. **Metric Card Creation**
   ```python
   def _create_metric_card(self, name, value, unit, color):
       # Return Gtk.Box with proper styling
   ```

4. **GSettings Integration** (if used)
   ```python
   settings = Gio.Settings.new("org.gnome.Pulse")
   # Bind preferences for period selector persistence
   ```

## Testing Strategy

### Unit Tests
- Test metric card creation
- Test period selector state management
- Test metric value formatting

### Integration Tests
- Test stats calculation with real GroupService
- Test UI updates on period change
- Test CSS class application

### Accessibility Tests
- Keyboard navigation (Tab, Shift+Tab)
- Focus indicators visible
- Screen reader compatibility (Orca)

## Next Steps After Phase 2

1. **Phase 2 Completion Review**
   - Read agent results and verify implementation
   - Run full test suite
   - Commit all changes

2. **Phase 3 Planning**
   - System integration (D-Bus, Quick Settings)
   - Search provider
   - Global shortcuts
   - Shell notifications

3. **Release Planning**
   - v0.3.0-alpha1 release
   - Community feedback collection
   - Bug fixes based on feedback

## Notes for Agent Integration

- All Phase 1 tests must still pass (151+ total)
- No modifications to core business logic (GroupService, GroupStatsService)
- Focus on UI/UX only
- All new code must be documented
- Keyboard accessible from day one
- CSS should follow existing patterns from styles_group.css

---

**Branch:** feature/v0.3.0-design-implementation
**Expected Completion:** ~60-120 minutes from agent start
**Quality Gates:** Lint 100%, Typecheck 100%, Tests 151+
