# Architecture Overview

PulseTask follows a modular architecture:

- Core: task model, timer engine, persistence
- Core: task model, timer engine, persistence, local observability metrics
- UI: GTK4/libadwaita presentation and interactions
- System: desktop integrations (notifications, sound, tray)

## Core Principle

Timer semantics are based on absolute timestamps:

remaining = target_timestamp - now

This improves resilience across app restarts and system suspend/resume.

## Boundaries

- Core does not depend on GTK.
- UI depends on Core contracts.
- System adapters are isolated for easier testing and replacement.

## Local Observability

PulseTask stores local counters in `~/.local/share/pulsetask/metrics.json`.

These counters track task lifecycle operations (create/start/pause/resume/expire/complete,
archive/delete/restore, and related block actions) to support local diagnostics
without external telemetry.
