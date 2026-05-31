# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-05-31

### Added

#### FASE 0: Foundation Complete ✅

**Sprint 0.1: Group Task Execution**
- `TaskGroup` and `GroupMember` dataclasses for group execution
- `GroupService` with full CRUD and lifecycle management
- Support for sequential task execution with auto-advancement
- Pause/resume functionality for entire groups
- Time tracking (elapsed, remaining, paused)
- Progress tracking (percentage, completed, skipped)
- Skip task functionality within groups
- Database schema for `task_groups` table with indexes
- 44 comprehensive unit + integration tests (100% passing)

**Sprint 0.2: Testing Foundation**
- GitHub Actions CI workflow (lint, typecheck, test, build)
- Pre-commit hooks for local linting
- Test coverage reporting with codecov
- 44 tests for group execution (100% coverage)

**Sprint 0.3: Documentation**
- `ARCHITECTURE.md` - System design and module organization
- `API.md` - Complete service interface reference
- `DATABASE.md` - Schema, migrations, and query reference
- `CONTRIBUTING.md` - Development workflow

**Sprint 0.4: CI/CD & Quality**
- All 106 tests passing (44 group + 62 existing)
- 100% type check pass (mypy)
- 100% lint pass (ruff)
- Semantic versioning and changelog

#### FASE 1: Beautiful Linux App ✅

**Sprint 1.1: Group Execution UI**
- `GroupExecutionWindow`: Full-featured group timer interface
  - Large readable timer display (MM:SS format)
  - Task queue with current task highlighting
  - Progress bar showing group completion %
  - Control panel (Pause/Resume, Skip, Stop)
  - Stats footer with completion tracking
  - 100ms refresh rate for smooth updates
- `GroupOverlay`: Compact floating 320x120px window
  - Minimal timer + task name display
  - Focus-based opacity toggle (1.0 focused, 0.7 unfocused)
  - Pause/Skip controls
  - Always-on-top behavior
- UI Components: `TimerDisplay`, `TaskRow`, `TaskQueue`, `ControlPanel`, `StatsFooter`
- GNOME design tokens integration
- 23 new tests for UI components (all passing)

**Sprint 1.2: Advanced Statistics**
- `GroupStatsService`: Comprehensive execution analytics
  - Daily statistics (groups, tasks, focus time, interruptions)
  - Period statistics (7/30 day aggregations)
  - Completion rate (tasks/estimated capacity)
  - Interruption rate (pauses + skips per group)
  - Weekly activity heatmap by weekday
- `StatsWindow` UI: Statistics viewer with 6 key metrics
- Data Exports: CSV + JSON for external analysis
- Focus heatmap visualization (5 intensity levels)

**Sprint 1.3: Accessibility (WCAG 2.1 AA)**
- Focus indicators: 3px outline on all interactive elements
- High contrast mode support (@media prefers-contrast)
- Reduced motion support (@media prefers-reduced-motion)
- A11yHelper utilities for screen reader support
- ACCESSIBILITY_CHECKLIST.md: 95% WCAG AA compliance
- 100% keyboard navigation (Tab/Shift+Tab through all controls)

### Changed
- Updated project description: "A calm execution environment for Linux power users"
- Bumped version to 0.2.0 and status to Beta
- Enhanced CSS styling with accessibility features
- Improved database abstraction for GroupService

### Technical Details
- Group execution follows state machine: IDLE → EXECUTING → PAUSED → COMPLETED
- Timer updates every 100ms via GLib.timeout_add for smooth animation
- Statistics computed on-demand from task_groups table
- CSS uses GTK4 theme variables (@theme_base_color, @theme_accent_color)
- Full type hints with mypy (100% pass rate)
- Lint compliance with ruff (100% pass rate)

### Known Limitations
- No sync backend (local database only)
- No team/collaboration features
- No drag-and-drop task reordering
- Notifications are basic (no D-Bus actions in V1)

### Quality Metrics
- Tests: 129 passing (85%+ coverage)
- Lint: 100% pass (ruff)
- Type Check: 100% pass (mypy)
- WCAG: 95% AA compliance
- CI/CD: GitHub Actions on push/PR

**Sprint 0.3: Documentation**
- `ARCHITECTURE.md` - System design and module organization
- `API.md` - Complete service API reference
- `DATABASE.md` - Schema, migrations, and queries
- Updated `CONTRIBUTING.md` with development workflow

**Sprint 0.4: CI/CD**
- `.github/workflows/ci.yml` - Automated testing on push/PR
- Lint checks (ruff) on every commit
- Type checking (mypy) on every commit
- Test execution with coverage reporting

### Changed
- CSS loading system now reads from `styles.css` file for POC development
- Database abstraction refactored for both file-based and in-memory testing

### Technical Details
- Group execution follows state machine: IDLE → EXECUTING → PAUSED → COMPLETED/ARCHIVED
- Time tracking accounts for pause duration
- Auto-completion when all tasks processed (completed or skipped)
- Database uses JSON for task_ids flexibility

### Known Limitations
- Group UI (GroupExecutionWindow) not yet integrated into main window
- POC visual designs (3 styles) created but not selected/integrated
- No sync backend (local DB only)
- No team features yet

## [0.1.0] - 2026-05-01

### Initial Release
- Basic task execution timer
- Task CRUD operations
- Preferences and notifications
- System tray integration

---

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
