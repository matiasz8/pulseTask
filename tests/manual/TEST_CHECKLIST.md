# Manual Test Checklist

## Platform

- [ ] Ubuntu 22.04+
- [ ] GNOME 42+
- [ ] Wayland session
- [ ] X11 session

## Timer Behavior

- [ ] Create task with fixed duration
- [ ] Start and verify countdown updates
- [ ] Pause and resume without large drift
- [ ] Restart app and verify running timer recovery
- [ ] Let task expire and verify state transition

## Alerts

- [ ] Completion notification appears
- [ ] Completion sound plays
- [ ] Alert actions (snooze/repeat/close) behave correctly

## Accessibility

- [ ] Keyboard-only flow can create/start/pause a task
- [ ] Focus indicators are always visible
- [ ] Screen reader labels are present

## Performance

- [ ] Startup below 2 seconds on reference machine
- [ ] Memory under 150MB during normal usage
