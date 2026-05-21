# PulseTask

Deadlines visible, focus real.

PulseTask is a modern Linux desktop task app for fixed-duration work sessions with highly visible countdowns and strong completion alerts.

## Why PulseTask

Most tools track elapsed time or generic pomodoros. PulseTask focuses on individual tasks with explicit deadlines:

- "Reply to inbox - 20 minutes"
- "Math study - 45 minutes"
- "Production deploy - 15 minutes"

## Current Status

Early implementation bootstrap.

Implemented in this first commit:

- Open-source collaboration baseline for GitHub
- English-first documentation and contribution workflow
- Core task domain model
- Absolute-timestamp timer engine
- SQLite task persistence
- Unit tests and CI baseline

MVP Block 1 status: completed.

- Preferences persistence (default duration, archived visibility, sound profile, close-to-tray)
- Destructive action safeguards (delete confirmation + undo for archive/delete)
- Expiration flow with configurable snooze options (1/5 min)

## Planned Stack

- Python 3.12+
- GTK4 + libadwaita (UI)
- SQLite (persistence)
- org.freedesktop.Notifications (desktop notifications)
- Flatpak as primary distribution

## Quick Start (uv + Makefile)

```bash
make venv
make sync
make ci
```

## Common Commands

```bash
make test
make lint
make typecheck
make run
make install-desktop
make flatpak-validate
make flatpak-build
make flatpak-install
make flatpak-run
```

`make install-desktop` installs a local desktop entry and icon so Ubuntu Dock shows PulseTask icon instead of the generic gear.

If PulseTask does not appear in the app grid immediately, run `make install-desktop` again, then open it from Activities as "PulseTask" and pin it to Dock.

Flatpak packaging baseline is available via `packaging/flatpak/com.matiasz8.pulsetask.json` and metadata in `resources/linux/com.matiasz8.pulsetask.metainfo.xml`.

## Project Structure

- `src/pulse_task/core`: domain model, timer logic, persistence
- `src/pulse_task/ui`: GTK4/libadwaita UI layer (scaffold)
- `src/pulse_task/system`: desktop integration adapters (scaffold)
- `tests`: unit/integration/manual test suites
- `.github`: workflows and contribution templates

## Collaboration

- Read CONTRIBUTING.md before opening a PR
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
9. Add local observability metrics.
10. Prepare V2 features (overlay, advanced stats, deeper GNOME integrations).

## License

MIT
