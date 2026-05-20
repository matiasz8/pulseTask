# Architecture Overview

PulseTask follows a modular architecture:

- Core: task model, timer engine, persistence
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
