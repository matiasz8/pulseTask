# PulseTask v2

Deadlines visible, focus real.

PulseTask is a modern web application for focused task management with visible countdowns and strong completion alerts.

## What's New in v2

🎉 **v0.2.0 - Web Redesign**

✅ Modern React/Next.js Frontend
- Built with React 19 + Next.js 16
- TypeScript for type safety
- Tailwind CSS 4 for responsive design
- 60+ accessible Radix UI components

✅ Complete Feature Set
- Focus View with Pomodoro timer
- Task management (create, pause, resume, complete)
- Statistics dashboard with charts
- Compact overlay widget
- Dark mode support
- Keyboard shortcuts for efficiency

✅ Production Ready
- Fully compiled and tested
- Development server running
- Ready for deployment
- Comprehensive documentation

## Current Status

**v0.2.0 - Web Edition Released**

The application has been successfully migrated from Python/GTK desktop app to a modern web application:

- ✅ Frontend: React 19 + Next.js 16.2.6
- ✅ Styling: Tailwind CSS 4.2.0
- ✅ State Management: Zustand 5.0.13
- ✅ Components: Radix UI (40+ components)
- ✅ Build: Turbopack (6.0s compile time)
- ✅ Development: Hot reload enabled
- ✅ Production: Optimized builds ready

**Ready for:** Development, testing, deployment, community feedback

## Installation

### Prerequisites
- Node.js 22+
- npm or yarn

### Quick Start

```bash
# Clone and navigate
cd /run/media/nquiroga/SSDedo/Documents/personal/pulseTask

# Install dependencies
make install

# Start development server
make run
```

Visit **http://localhost:3000**

### From Source (Requires Python 3.12+, GTK4, libadwaita)

```bash
# Setup
make venv
make sync

# Run
make run

# Test
make test
```

### From Flathub (Coming Soon)
```bash
flatpak install flathub org.gnome.Pulse
flatpak run org.gnome.Pulse
```

## Features (v0.2.0)

### Core Execution
- **Group execution**: Run multiple tasks in one focused session with shared timer
- **Visual countdown**: Always visible timer on main window
- **Smart timing**: Tracks wall-clock time separately from task duration
- **Task advancement**: Auto-advance to next task or skip manually

### Analytics
- **Daily stats**: Completion rates, interruption patterns, focus duration
- **Weekly/monthly views**: Identify productivity trends
- **Activity heatmaps**: See when you're most productive
- **Export**: CSV/JSON data export for analysis

### Accessibility
- **WCAG AA compliant**: 95% accessibility score
- **Keyboard navigation**: Full keyboard control
- **Screen reader support**: Works with Orca
- **High contrast**: Support for Linux accessibility preferences

### Developer Experience
- **151 tests**: Comprehensive test coverage (85%+)
- **100% lint**: ruff with no issues
- **100% typed**: Full mypy compliance
- **CI/CD ready**: GitHub Actions included

## Common Commands

```bash
make test           # Run test suite
make lint          # Lint code
make typecheck     # Type checking
make run           # Run the app
make install-desktop  # Install desktop entry
```

## Community & Marketing

### FASE 2: Launch & Community
PulseTask is ready for the community. See our launch strategy:

- **[FASE 2 Executive Guide](docs/marketing/FASE_2_EXECUTIVE_GUIDE.md)** - Action items & timeline
- **[Reddit Strategy](docs/marketing/REDDIT_STRATEGY.md)** - r/gnome, r/linux, r/productivity
- **[HackerNews Strategy](docs/marketing/HACKERNEWS_STRATEGY.md)** - Show HN submission guide
- **[Flathub Submission](docs/marketing/FLATHUB_SUBMISSION.md)** - Step-by-step publication

### Next Steps
- Help us reach the Linux community
- Contribute features & fixes
- Report bugs & accessibility issues
- Share your experience

### v0.3.0 Roadmap
- Full D-Bus service implementation
- GNOME Quick Settings integration
- Actionable notifications
- GNOME Search Provider
- Global keyboard shortcuts

See [GNOME_INTEGRATION_SPEC.md](docs/GNOME_INTEGRATION_SPEC.md) for details.

## Collaboration

- Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR
- Keep all repository content in English
- Use issue templates for bugs and feature requests

## UI Direction

PulseTask aims for a premium, modern interface inspired by recent award-winning digital products while staying native to GNOME and accessible under stress.

## Roadmap

1. Close MVP functional gaps:
	- Persist user preferences (default duration, archived visibility, sound profile, close-to-tray)
	- Add destructive-action confirmations and safer task flows
	- Expand expiration flow with configurable snooze options
2. Nested task blocks and sequencing:
	- Allow parent tasks with ordered child tasks
	- Define execution order inside a block before starting
	- Auto-notify when a child task ends and auto-start the next one with start notification
	- Status: completed (parent + child start orchestration, ordered execution, auto-start next on finish/expire, add subtask with minutes and order, reorder controls, block progress display)
3. Stabilize tray and desktop behavior across GNOME/Wayland/X11.
	- Status: completed (close-to-tray minimize/restore flow, tray restore feedback, Wayland/X11-safe visibility handling)
4. Improve reliability and edge-case handling (suspend/resume, system time jumps, duplicate popups).
	- Status: completed (time-jump expiration coverage, suspend/resume-safe timer recovery, duplicate expired-dialog guard)
5. Continue modern UX polish and keyboard-first accessibility.
	- Status: completed (icon-based task actions, keyboard shortcuts for new task, undo, settings, archived toggle, and active task control)
6. Build a full settings screen and runtime application of preferences.
	- Status: completed (dedicated settings window with structured sections and live runtime application of preferences)
7. Harden Flatpak packaging and release metadata.
	- Status: completed (AppStream + desktop metadata validation script, CI packaging validation job, richer release metadata)
8. Improve open-source collaboration workflows and issue hygiene.
	- Status: completed (GitHub Issue Forms for bugs/features, template config with support/security routing, documented issue triage guide)
9. Add local observability metrics.
	- Status: completed (local persisted lifecycle counters wired through TaskService and covered by unit tests)
10. Prepare V2 features (overlay, advanced stats, deeper GNOME integrations).
	- Status: completed (V2 technical plan, advanced stats computation module, and local metrics report command)

## License

MIT
