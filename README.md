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
```

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

## License

MIT
