# Design PRD: PulseTask V2

Version: 1.0
Date: 2026-05-21
Owner: Product + Design
Product: PulseTask (Linux desktop app)

## 1. Product Context

PulseTask is a Linux desktop productivity app focused on fixed-duration tasks with visible deadlines.
It is not a generic pomodoro app. It is task-deadline first.

Current product baseline already includes:

- Full task lifecycle (create, start, pause, resume, reset, complete, archive, delete).
- Block workflows with ordered subtasks and automatic sequencing.
- Expiration alerts with sound and desktop notifications.
- Tray behavior handling across Linux desktop sessions.
- Runtime settings window.
- Local lifecycle metrics persistence.
- Packaging and metadata validation for release workflows.

V2 goal is to evolve from task timer into a focused execution system with stronger ambient UX and actionable insights.

## 2. Problem Statement

Users can execute tasks well today, but they still need:

- Lower-friction focus mode while multitasking.
- Better understanding of their execution patterns over time.
- More fluid desktop-native control surfaces for quick actions.

## 3. Vision

Deliver a native Linux focus experience where the active deadline is always accessible, progress quality is measurable, and interactions remain minimal under pressure.

## 4. Goals

1. Introduce an always-available Overlay Mode for active work sessions.
2. Provide Advanced Stats based on local metrics to improve self-management.
3. Expand GNOME-native interaction quality without compromising simplicity.
4. Preserve keyboard-first usability and accessibility as first-class constraints.

## 5. Non-Goals

- No cloud sync in this phase.
- No team collaboration features.
- No mobile companion.
- No redesign that breaks native GNOME behavior conventions.

## 6. Target Users

1. Individual Linux users doing deep work in focused intervals.
2. Developers/knowledge workers managing high-pressure short tasks.
3. Keyboard-first users who need low-friction, low-noise workflows.

## 7. User Jobs To Be Done

1. While working across windows, I need to always see remaining time without losing context.
2. After several sessions, I need to understand if I complete tasks or let them expire.
3. During active work, I need to trigger key actions in one step with minimal UI overhead.

## 8. Success Metrics

1. Overlay adoption rate among active users.
2. Weekly completion rate trend.
3. Expiration rate trend.
4. Resume-after-pause rate.
5. Median interaction count for start/pause/resume flows.
6. Qualitative usability score from keyboard-first users.

## 9. Functional Scope

1. Overlay Mode

- Compact always-on-top window for current task.
- Displays task title, remaining time, status, and quick actions.
- Quick actions: pause/resume, complete, snooze when applicable, open full app.
- Supports compact and ultra-compact density modes.
- Keyboard shortcut to toggle overlay visibility.

2. Advanced Stats

- Stats dashboard in app.
- Time windows: today, 7 days, 30 days.
- Core indicators: started, completed, expired, paused, resumed, snoozed, recovered.
- Derived ratios: completion rate, expiration rate, resume-after-pause rate.
- Trend visualization: simple line/bar components.

3. GNOME-Integrated Enhancements

- Actionable desktop notifications for task lifecycle actions.
- Stronger quick-access patterns through tray/launcher actions where available.
- Smooth state consistency after suspend/resume and session transitions.

## 10. UX and Visual Requirements

1. Design principles

- Clarity under pressure.
- One primary action per state.
- Progressive disclosure.
- Strong hierarchy for countdown and task status.

2. Interaction requirements

- Overlay must be operable in under 2 clicks for primary actions.
- Focus transitions must be visually calm and deterministic.
- Expiration state must be unmistakable but not visually chaotic.

3. Accessibility requirements

- High contrast compliance for critical timer/status information.
- Visible focus indicators in all interactive elements.
- Full keyboard navigation for all V2 features.
- Clear labels suitable for assistive technologies.

4. Platform requirements

- Native-feeling GNOME/libadwaita visual language.
- Behavior-safe for Wayland and X11 environments.
- Avoid web-like UI paradigms that conflict with desktop patterns.

## 11. Content and Tone

- Product copy in English.
- Direct, concise microcopy.
- Avoid motivational fluff in critical alerts.
- Prioritize action clarity over decorative language.

## 12. Design Deliverables

1. Information architecture for V2 surfaces.
2. User flows for Overlay, Stats, and quick actions.
3. High-fidelity screens for:

- Main app with stats entry point.
- Overlay compact mode.
- Overlay ultra-compact mode.
- Stats dashboard states (empty, populated, filtered range).
- Expiration and interruption states.

4. Component specs:

- Timer display variants.
- Status badges.
- Action button hierarchy.
- Notification action model.

5. Design tokens:

- Color roles by status.
- Typography scale.
- Spacing scale.
- State/interaction motion guidance.

6. Accessibility checklist and keyboard map.
7. Handoff annotations for engineering.

## 13. Technical Constraints for Design

- Frontend implementation is GTK4 + libadwaita.
- Data source for stats is local lifecycle counters already persisted.
- Current architecture is modular (core, UI, system adapters); avoid designs requiring monolithic rewrites.
- Feature should be incrementally shippable with low regression risk.

## 14. Release Strategy

1. V2.1

- Overlay mode baseline + shortcut + quick actions.

2. V2.2

- Advanced stats dashboard with core ratios and trend views.

3. V2.3

- Enhanced GNOME actionable integrations and UX polish pass.

## 15. Acceptance Criteria

1. Overlay can be toggled quickly and stays readable under real multitasking.
2. Core stats are understandable without documentation.
3. Keyboard-only users can complete primary V2 flows.
4. No regressions in existing task/block sequencing behavior.
5. V2 UX changes include before/after evidence and rationale.

## 16. Open Questions

1. Should overlay be per-task only, or support mini queue preview?
2. What is the default overlay density mode?
3. Which quick actions are safe to expose directly in notifications?
4. Should stats include session quality tags in V2 or defer to later phase?
