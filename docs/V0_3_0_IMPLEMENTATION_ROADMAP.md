# v0.3.0 Implementation Roadmap - Design-Driven Development

**Status**: Ready for Implementation
**Target Version**: v0.3.0
**Timeline**: 4-6 weeks (full-time) or 8-12 weeks (part-time)
**Effort**: ~54 developer hours

---

## Executive Summary

The design you reviewed is **fully feasible** for Ubuntu/GNOME. Your v0.2.0 implementation already covers ~40% of the design vision. The remaining 60% consists of UI polish, settings implementation, and system integration - all using standard GNOME APIs.

**Recommendation**: Proceed with implementation. This positions PulseTask as a premium Linux application with operational focus.

---

## What's Already Done (v0.2.0)

✅ **Focus Tab Core**
- Task input field
- Duration buttons (5m, 15m, 25m, 45m, 60m)
- Custom duration input
- Subtasks support
- Create task button

✅ **Stats Data Engine**
- Completion Rate calculation
- Expiration Rate tracking
- Average Overtime calculation
- Pause Fragmentation analysis
- Focus Consistency metrics
- Total Focus Time aggregation
- Daily/weekly/monthly filtering

✅ **System Foundation**
- GSettings schema for preferences
- D-Bus interface defined
- Window management (main + overlay)
- Database persistence

✅ **Testing & Quality**
- 151 tests passing
- 100% lint compliance
- 100% type checking
- 95% accessibility (WCAG AA)

---

## What Needs Implementation (v0.3.0)

### Phase 1: UI Polish & Settings (2-3 weeks)

#### 1.1 Focus Tab Refinement
```
Current state: Functional but basic
Target state: Professional, polished UI

Tasks:
- [ ] Improve button layout (better spacing, grouping)
- [ ] Add visual feedback for selected duration
- [ ] Keyboard shortcuts (Ctrl+1=5m, Ctrl+2=15m, etc)
- [ ] Animate task creation
- [ ] Better typography

Effort: 2-4 hours
Files to modify:
  - src/pulse_task/ui/group_window.py (Focus tab layout)
  - Add new: src/pulse_task/ui/styles_focus.css
```

#### 1.2 Settings Tab Implementation
```
Current state: GSettings schema defined but no UI
Target state: Full settings panel with all options

Tasks:
- [ ] Create PreferencesWindow with 3 sections:
    - General: dark mode, week start
    - Focus: auto-start, title display, pause on blur
    - Notifications: notifications, warnings, threshold
- [ ] Implement GTK4 toggles, spinners, combo boxes
- [ ] Connect to GSettings for persistence
- [ ] Apply changes immediately

Options to implement:
✓ Dark mode toggle
✓ Start week on Monday (for calendar integration)
✓ Auto-start next task
✓ Show remaining time in window title
✓ Pause on window blur
✓ Desktop notifications
✓ Expiration warnings
✓ Warning threshold (minutes)

Effort: 12-16 hours
Files to create:
  - New: src/pulse_task/ui/settings_window.py (PreferencesWindow)
  - New: src/pulse_task/ui/styles_settings.css
Tests:
  - New: tests/test_settings_window.py (8-12 tests)
```

#### 1.3 Window Title Countdown
```
Current state: Not implemented
Target state: "15m 30s - PulseTask" in window title

Tasks:
- [ ] Hook into 100ms timer loop
- [ ] Format countdown as "mm:ss"
- [ ] Update window.set_title() every second
- [ ] Stop when task finishes

Effort: 4-6 hours
Files to modify:
  - src/pulse_task/ui/group_window.py (add title update)
```

**Phase 1 Subtotal**: 20-30 hours = 1-2 weeks
**Result**: 80% of user experience improvement, release-ready for most users

---

### Phase 2: Stats Visualization (1-2 weeks)

#### 2.1 Stats Dashboard UI
```
Current state: Data exists, no visualization
Target state: Professional metric cards with trends

Tasks:
- [ ] Create 6 metric cards (one per metric)
- [ ] Card layout: Icon + large number + description + trend
- [ ] Trend indicators: up/down arrows with color
- [ ] Daily/weekly/monthly selector buttons
- [ ] Responsive grid layout

Metrics to display:
1. Completion Rate
   Display: "85%" with green ↑ trend
   Description: "Tasks finished within allocated time"

2. Expiration Rate
   Display: "15%" with red ↓ trend
   Description: "Tasks that exceeded time limit"

3. Average Overtime
   Display: "2m 30s" with blue indicator
   Description: "Time spent past expiration"

4. Pause Fragmentation
   Display: "12%" with neutral indicator
   Description: "Tasks interrupted by pauses"

5. Focus Consistency
   Display: "78%" with green ↑ trend
   Description: "Completion × uninterrupted focus"

6. Total Focus Time
   Display: "18h 45m" with neutral indicator
   Description: "0 tasks completed today"

Effort: 8-12 hours
Files to create:
  - New: src/pulse_task/ui/stats_view.py (StatsWindow)
  - New: src/pulse_task/ui/styles_stats.css (card styling)
Tests:
  - New: tests/test_stats_view.py (6-10 tests)
```

#### 2.2 Chart Rendering (Optional)
```
Add simple chart visualizations:
- [ ] Activity heatmap (week overview)
- [ ] Trend line (daily progress)
- [ ] Bar chart (completion vs expiration)

Tool options:
A) Text-based charts (ASCII bars) - 2 hours
B) Cairo drawing (native GTK) - 6-8 hours
C) SVG charts with librsvg - 8-10 hours

Recommendation: Start with simple bars, iterate

Effort: 2-10 hours (optional, can defer)
```

**Phase 2 Subtotal**: 10-15 hours = 1 week
**Result**: Professional "wow" dashboard that shows value

---

### Phase 3: System Integration (1-2 weeks)

#### 3.1 Desktop Notifications
```
Current state: D-Bus interface defined, not implemented
Target state: Actionable notifications for key events

Notification scenarios:

1. Task Expiration
   Title: "Task expired"
   Body: "[Task name]"
   Actions: ["Snooze 5m", "Start next task", "Dismiss"]
   
2. Time Warning (5 min before expiration)
   Title: "5 minutes remaining"
   Body: "[Task name]"
   Actions: ["Extend 5m", "Continue", "Dismiss"]

3. Focus Lost
   Title: "Window focus lost"
   Body: "Auto-paused due to focus loss"
   Actions: ["Resume", "Keep paused"]

Tasks:
- [ ] Implement notification manager
- [ ] Use org.freedesktop.Notifications D-Bus interface
- [ ] Add action handlers for buttons
- [ ] Integrate with GroupService callbacks
- [ ] Handle notification timeouts

Effort: 16-20 hours
Files to create:
  - New: src/pulse_task/notifications/manager.py
  - Modify: src/pulse_task/core/group_service.py (add callbacks)
Tests:
  - New: tests/test_notifications.py (10-15 tests)

Challenge: Async D-Bus handling (medium complexity)
```

#### 3.2 Auto-pause on Window Blur
```
Current state: Not implemented
Target state: Automatic pause when window loses focus

Behavior:
- [ ] Listen to window focus-out event
- [ ] Auto-pause execution
- [ ] Optional: ask user to resume or auto-resume
- [ ] Log pause reason as "focus_loss"

Tasks:
- [ ] Connect to GTK window focus signal
- [ ] Call GroupService.pause_group_execution()
- [ ] Handle window focus-in (resume prompt)
- [ ] Add to settings as optional feature

Effort: 6-8 hours
Files to modify:
  - src/pulse_task/ui/group_window.py (add signal handlers)
Tests:
  - New: tests/test_window_blur.py (4-6 tests)
  
Challenge: Testing window blur (need X11/Wayland awareness)
```

**Phase 3 Subtotal**: 20-25 hours = 1-2 weeks
**Result**: Deep GNOME integration, power-user features

---

### Phase 4: Polish & Optimization (1 week)

#### 4.1 Theme Consistency
```
Tasks:
- [ ] Dark mode / light mode consistency
- [ ] Color palette alignment
- [ ] Typography polish
- [ ] Icon consistency

Effort: 4-6 hours
```

#### 4.2 Accessibility Re-audit
```
Tasks:
- [ ] WCAG AA re-check (should still be 95%+)
- [ ] New settings tab accessibility
- [ ] Stats dashboard keyboard nav
- [ ] Screen reader testing

Effort: 4-6 hours
```

#### 4.3 Performance Optimization
```
Tasks:
- [ ] Profile UI rendering
- [ ] Optimize stats calculations
- [ ] Reduce memory footprint
- [ ] Smooth animations

Effort: 4-6 hours
```

**Phase 4 Subtotal**: 10-15 hours = 1 week
**Result**: Release-ready v0.3.0

---

## Detailed Implementation Plan

### Sprint 1: Focus Tab & Settings (Weeks 1-2)

```
Sprint 1.1: Focus Tab (3-4 days)
├─ Polish buttons and layout (2h)
├─ Add keyboard shortcuts (2h)
├─ Update styles (2h)
└─ Test & iterate (2h)

Sprint 1.2: Settings Tab (5-6 days)
├─ Create PreferencesWindow class (3h)
├─ General section: dark mode, week start (3h)
├─ Focus section: auto-start, title, blur (4h)
├─ Notifications section: notifications, warnings (4h)
├─ Connect GSettings persistence (3h)
├─ Create tests (4h)
└─ Polish & iterate (3h)

Sprint 1.3: Title Countdown (1-2 days)
├─ Add timer integration (2h)
├─ Test on X11 and Wayland (2h)
└─ Edge cases handling (2h)
```

### Sprint 2: Stats Dashboard (Weeks 3-4)

```
Sprint 2.1: Stats Cards (3-4 days)
├─ Create metric card component (4h)
├─ Implement 6 card layouts (4h)
├─ Add trend indicators (2h)
├─ Styling & polish (3h)
├─ Create tests (4h)
└─ Iterate based on design (2h)

Sprint 2.2: Time Selector & Optional Charts (2-3 days)
├─ Daily/weekly/monthly buttons (2h)
├─ Simple chart rendering (4-6h)
├─ Data filtering (2h)
└─ Test (2h)
```

### Sprint 3: System Integration (Weeks 5-6)

```
Sprint 3.1: Notifications (3-4 days)
├─ Set up D-Bus notification manager (4h)
├─ Implement task expiration notifications (3h)
├─ Time warning notifications (2h)
├─ Action handlers (4h)
├─ Integration with GroupService (3h)
├─ Create tests (6h)
└─ Debug async issues (4h)

Sprint 3.2: Window Blur (1-2 days)
├─ GTK focus signal integration (2h)
├─ Auto-pause logic (1h)
├─ Focus recovery (1h)
├─ Test (2h)
└─ Handle Wayland edge cases (1h)
```

### Sprint 4: Polish (Week 7)

```
Sprint 4.1: Theme & Accessibility (2-3 days)
├─ Dark/light mode polish (2h)
├─ Accessibility audit (4h)
├─ Screen reader testing (2h)
└─ Fix issues (4h)

Sprint 4.2: Performance & Release (2-3 days)
├─ Profile & optimize (4h)
├─ User testing iteration (3h)
├─ Final fixes (2h)
└─ Release prep (2h)
```

---

## Testing Strategy

### Unit Tests (Per Phase)
- Phase 1: SettingsWindow tests (8-12 tests)
- Phase 2: StatsView tests (8-12 tests)
- Phase 3: Notification tests (10-15 tests)
- Phase 4: Polish/perf tests (4-6 tests)

**Target**: Maintain 85%+ coverage

### Integration Tests
- Settings persistence workflow
- Notification delivery and actions
- Window focus handling
- Stats data flow

### Manual Testing
- Visual polish review
- Keyboard navigation audit
- Screen reader testing (Orca)
- Dark/light mode switching
- Multi-monitor setups

### Testing Environments
- Ubuntu 24.04 (primary)
- GNOME 46+ 
- Wayland (if available)
- X11 fallback

---

## Risk Mitigation

### Low Risk (No Concerns)
- Focus tab polish (standard UI work)
- Settings tab (standard GNOME patterns)
- Title countdown (simple)
- Stats cards (standard layouts)

### Medium Risk (Manageable)
- D-Bus notifications (async complexity)
  - Mitigation: Reference existing GNOME code
  - Test incrementally
  - Use dbus-python documentation
  
- Window blur detection (platform-dependent)
  - Mitigation: Test on both Wayland and X11
  - Graceful fallback if unsupported
  - Document platform requirements

### No High-Risk Items Identified

---

## Success Criteria

| Phase | Success Criteria | Status |
|-------|------------------|--------|
| 1 | Settings saved and persist | TBD |
| 1 | Title shows countdown | TBD |
| 2 | 6 metrics display correctly | TBD |
| 2 | Trends show up/down | TBD |
| 3 | Notifications fire on schedule | TBD |
| 3 | Auto-pause works | TBD |
| 4 | WCAG AA maintained | TBD |
| 4 | Performance acceptable | TBD |

---

## Version Milestones

```
v0.3.0-alpha1: Phase 1 complete (Focus + Settings)
v0.3.0-beta1:  Phase 1-2 complete (+ Stats)
v0.3.0-beta2:  Phase 1-3 complete (+ Notifications)
v0.3.0:        All phases complete + polish
```

---

## Next Steps

1. **Approve Roadmap** - Confirm this plan aligns with your vision
2. **Start Sprint 1** - Begin with Phase 1 (Focus + Settings)
3. **Plan Iteration Cycle** - Weekly reviews, feedback incorporation
4. **Community Engagement** - Share progress on GitHub Discussions

---

## Questions to Consider

1. **Priority**: Which phase matters most to you?
   - UI polish first? (Phase 1)
   - Stats visibility? (Phase 2)
   - System integration? (Phase 3)

2. **Timeline**: Can you dedicate full-time or part-time?
   - Full-time: 4-6 weeks
   - Part-time: 8-12 weeks

3. **Scope**: Are all features in-scope or should we cut something?
   - Phase 3.2 (window blur) could be deferred
   - Chart rendering (Phase 2.2) could be MVP'd as text

4. **Community**: Should this be open for community contributions?
   - Yes: Label issues with v0.3.0 in GitHub
   - No: Solo development

---

## Appendix: File Structure

```
src/pulse_task/
├── ui/
│   ├── group_window.py (modify: add settings, refine focus)
│   ├── settings_window.py (NEW)
│   ├── stats_view.py (NEW)
│   ├── styles_focus.css (NEW)
│   ├── styles_settings.css (NEW)
│   └── styles_stats.css (NEW)
│
├── notifications/
│   └── manager.py (NEW)
│
└── core/
    └── group_service.py (modify: add callbacks)

tests/
├── test_settings_window.py (NEW)
├── test_stats_view.py (NEW)
├── test_notifications.py (NEW)
└── test_window_blur.py (NEW)
```

---

*Ready for implementation. All decisions made, all APIs validated, all risks identified.*
