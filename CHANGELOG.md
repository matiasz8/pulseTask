# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-01

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
