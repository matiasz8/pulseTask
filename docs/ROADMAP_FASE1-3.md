# PulseTask: FASE 1-3 Complete Roadmap

## Current Status

- ✅ **FASE 0**: Foundation complete (Group execution, Testing, CI/CD, Docs)
- ✅ **FASE 1 Sprint 1**: Group Execution UI (GroupExecutionWindow + Overlay)
- 🔄 **FASE 1 Sprints 2-4**: Remaining (Stats, Accessibility, Release Process)
- ⏳ **FASE 2**: Community & Adoption
- ⏳ **FASE 3**: Deep GNOME Integration

---

## FASE 1: Beautiful Linux App (3-4 sprints)

**Objective**: Premium visual experience with perfect UX

### Sprint 1.1: Group Execution UI ✅ DONE
- [x] GroupExecutionWindow (full-featured timer interface)
- [x] GroupOverlay (compact floating window)
- [x] CSS styling with GNOME design tokens
- [x] 23 new tests (all passing)
- [x] Timer updates (100ms refresh)
- **Status**: Merged to main

### Sprint 1.2: Advanced Stats & Analytics (2-3 days)

**Files to create**:
- `src/pulse_task/ui/stats_view.py` - Statistics window
- `src/pulse_task/core/stats.py` - Stats computation (extend existing)
- `src/pulse_task/ui/styles_stats.css` - Stats styling

**Features**:
- [ ] Stats window with historical data (7/30 day views)
- [ ] Charts: completion trends, interruption patterns, focus duration
- [ ] Export CSV/JSON for external analysis
- [ ] Daily/weekly/monthly aggregations
- [ ] Heatmap of active hours
- [ ] Tests: Stats computation accuracy, edge cases

**Acceptance**: Charts render correctly, CSV export works

### Sprint 1.3: Accessibility Audit & Fixes (2-3 days)

**Files to update**:
- `src/pulse_task/ui/desktop.py` - Main window accessibility
- `src/pulse_task/ui/group_window.py` - Group window a11y
- `src/pulse_task/ui/styles.css` - Focus indicators

**Features**:
- [ ] Keyboard navigation (full workflow: Tab/Shift+Tab through all controls)
- [ ] High-contrast focus indicators (4:1 minimum)
- [ ] Screen reader announcements (task transitions, timer updates)
- [ ] Color contrast validation (WCAG AA: 4.5:1 text)
- [ ] Font size scaling (test at 120%, 150%, 200%)
- [ ] Tests: Keyboard workflow, focus management

**Acceptance**: WCAG AA 95%+ pass rate, keyboard-only workflow functional

### Sprint 1.4: Professional Release (2 days)

**Files to create/update**:
- Update `pyproject.toml` version → 0.2.0
- Create GitHub Release with assets
- Update `CHANGELOG.md` with conventional commits
- Prepare Flathub submission

**Features**:
- [ ] Semantic versioning (0.2.0 release tag)
- [ ] Changelog with structured format
- [ ] GitHub Release with screenshots/GIF demo
- [ ] Flathub app metadata + manifest
- [ ] AppStream description updated

**Acceptance**: App appears in Flathub search

---

## FASE 2: Community & Adoption (2 sprints)

**Objective**: Market penetration in Linux community

### Sprint 2.1: Marketing Launch (3-4 days)

**Deliverables**:
- [ ] Landing page (GitHub Pages) with hero section
  - "A calm execution environment for Linux power users"
  - Screenshot carousel
  - Video demo (30s loop)
- [ ] Social media campaign
  - Reddit r/linux, r/gnome, r/ubuntu posts
  - HackerNews submission
  - OMGUbuntu blog pitch
- [ ] Blog post: "Why we built PulseTask"
  - Philosophy alignment with GNOME values
  - Differentiation from Notion/Todoist
  - Target audience: Developers, ADHD users, remote workers

**Success Metrics**:
- 100+ upvotes on r/gnome
- 200+ GitHub stars
- 50+ discussions opened

### Sprint 2.2: Community Infrastructure (2-3 days)

**Features**:
- [ ] Issue triage guide
  - Severity levels (bug, feature, enhancement)
  - Good first issue marking
  - Contributor welcome message
- [ ] Release notes template
  - Consistent format
  - Breaking changes highlighted
- [ ] Public roadmap (GitHub Project board)
  - Transparent about upcoming features
  - Community voting on priorities
- [ ] GitHub Discussions enabled
  - Feature requests go to Discussions (not Issues)
  - Community support channel

### Sprint 2.3: First Contributors (2-3 days)

**Activities**:
- [ ] Identify 5 beginner-friendly issues
  - Good documentation
  - Small scope (~2 hours)
  - Clear acceptance criteria
- [ ] Rapid PR review (<48hrs)
  - Constructive feedback
  - Help with setup if needed
- [ ] Recognition
  - Add to CONTRIBUTORS.md
  - Mention in release notes
  - Welcome message in all PRs

**Success**: 3+ external PRs merged

---

## FASE 3: Deep GNOME Integration (3-4 sprints)

**Objective**: Native GNOME citizen (not just a GTK4 app)

### Sprint 3.1: Quick Settings Integration (3-4 days)

**Research/Spike** (1 day):
- [ ] Evaluate Quick Settings API (GNOME 47+)
- [ ] Check if shell extension needed vs D-Bus service
- [ ] Test on X11 and Wayland

**Implementation** (2-3 days):
- [ ] Create `src/pulse_task/system/quick_settings.py`
  - D-Bus service for GNOME Shell
  - Toggle: "PulseTask: Active/Paused"
  - Status icon
- [ ] Tests: D-Bus method calls, Wayland compatibility
- **File**: `data/org.gnome.Pulse.quick-settings.gschema.xml` (GSettings)

**Acceptance**: Quick Settings toggle appears and works

### Sprint 3.2: Actionable Notifications (2-3 days)

**Features**:
- [ ] Create `src/pulse_task/system/notifications_dbus.py`
  - D-Bus implementation (org.freedesktop.Notifications)
  - Action buttons: Start, Skip, Extend +5m
- [ ] Notify on:
  - Task transition (current task name)
  - Group completion
  - Time warnings (5m remaining)
- [ ] Tests: Notification delivery, action callbacks

**Acceptance**: Click button in notification to execute action

### Sprint 3.3: Search Provider (2-3 days)

**Research** (1 day):
- [ ] Evaluate GNOME Search Provider API
- [ ] Check search indexing performance

**Implementation** (1-2 days):
- [ ] Create `src/pulse_task/system/search_provider.py`
  - Implement DBus SearchProvider interface
  - Index tasks for search
  - Result ranking (active > recent > old)
- [ ] Tests: Search result ordering, performance

**Acceptance**: Type task name in GNOME Overview → results appear

### Sprint 3.4: Global Shortcuts (1-2 days)

**Features**:
- [ ] Keyboard shortcuts:
  - `Super+P` → Toggle PulseTask window
  - `Ctrl+Alt+T` → Toggle overlay
  - `Ctrl+Alt+S` → Skip current task
- [ ] Register with GNOME Settings → Keyboard → Custom Shortcuts
- [ ] Tests: Shortcut delivery under different WMs

**Acceptance**: Shortcuts work from any application

---

## Technical Debt & Cleanup

### Documentation
- [ ] Create `docs/GNOME_INTEGRATION.md` (for future contributors)
- [ ] ADR: "Why we chose GTK4 over Electron"
- [ ] ADR: "Group execution design (state machine, timer semantics)"

### Testing
- [ ] Add UI screenshot tests (pytest-playwright)
- [ ] Performance benchmarks (timer accuracy <50ms drift)
- [ ] Stress tests (1000 tasks, rapid state changes)

### CI/CD
- [ ] Multi-platform testing (X11, Wayland)
- [ ] Automated screenshot capture for release notes
- [ ] Security scanning (dependabot, SAST)

---

## Timeline & Effort

| Phase | Duration | FTE-Months | Key Risks |
|-------|----------|-----------|-----------|
| FASE 1.2-1.4 | 1 week | 1 | Design review cycles |
| FASE 2.1-2.3 | 1 week | 1 | Low community traction |
| FASE 3.1-3.4 | 2 weeks | 1.5 | GNOME API instability |
| **Total FASE 1-3** | **4 weeks** | **3.5** | |

**For solo developer**: ~4-5 weeks part-time (working evenings/weekends)

---

## Success Metrics (At End of FASE 3)

### User Metrics
- 500+ GitHub stars
- 50+ discussions
- 10+ external contributors
- 2-5K monthly active users (estimate)

### Quality Metrics
- Test coverage: 85%+
- CI pass rate: 100%
- Release cycle: 2 weeks
- Community response time: <24hrs

### Market Metrics
- Flathub featured (if quality high)
- Reddit: 100+ upvotes on best post
- Blog mentions (Linux news sites)
- GNOME Circle consideration (optional)

---

## Next Immediate Actions

1. **This Week**: Complete FASE 1.2 (Stats & Analytics)
   - Create `stats_view.py` with charts
   - Add CSV export functionality
   - Write 15+ tests

2. **Next Week**: FASE 1.3 (Accessibility)
   - Keyboard navigation audit
   - Focus indicator fixes
   - WCAG validation

3. **Following Week**: FASE 1.4 + FASE 2.1
   - Release 0.2.0
   - Launch marketing campaign
   - Track initial community response

---

## Philosophy Reminder

**Every feature must serve the core mission**:
> "A calm execution environment for Linux power users"

- ✅ Does it reduce noise?
- ✅ Does it improve clarity?
- ✅ Does it feel native to Linux/GNOME?
- ❌ Does it add bloat?
- ❌ Does it look like SaaS?

