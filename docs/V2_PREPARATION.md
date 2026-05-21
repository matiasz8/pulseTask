# V2 Preparation Plan

This document captures the implementation-ready preparation for V2 scope.

## Scope Prepared in Block 10

- Overlay mode groundwork
- Advanced stats groundwork
- Deeper GNOME integration roadmap

## Overlay Mode (Foundation)

Target outcome for V2 implementation:

- Compact always-visible timer surface for active task
- Optional "focus mode" display profile
- Fast keyboard toggle between full window and overlay

Preparation completed:

- Existing absolute-timestamp timer model and one-running-task policy already support overlay rendering semantics.
- Runtime settings infrastructure can host overlay toggles without architectural changes.

## Advanced Stats (Foundation)

Target outcome for V2 implementation:

- Show completion/expiration trends over time
- Expose interruption and recovery indicators
- Offer local-only export-friendly stats snapshot

Preparation completed:

- Local lifecycle counters are persisted in `~/.local/share/pulsetask/metrics.json`.
- `pulse_task.core.stats` computes derived productivity ratios from counters.
- `pulsetask-metrics` CLI provides a text report for diagnostics and future UI integration.

## GNOME Integrations (Roadmap)

Target outcome for V2 implementation:

- Better shell integration for notifications and quick actions
- Optional richer integration points where desktop supports them

Planned spikes:

1. Evaluate Quick Settings and shell extension integration boundaries.
2. Prototype actionable notifications with task controls.
3. Verify behavior under GNOME Wayland and X11 fallback paths.

## Validation Readiness

For V2 implementation PRs:

- Keep core logic UI-agnostic.
- Add unit tests for any derived stats logic.
- Include before/after captures for overlay UX changes.
- Maintain English-first docs/issues/PR descriptions.
