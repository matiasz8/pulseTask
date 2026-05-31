# Contributing to PulseTask

Welcome! PulseTask is a **calm execution environment for Linux power users**. We build with intention—not every feature request becomes a feature. This guide will help you contribute in ways that align with our philosophy.

## Our Philosophy

- **Constraint breeds clarity**: We do one thing exceptionally well
- **Calm over flashy**: No gamification, notifications, or AI hype
- **Linux-native**: GNOME design, GTK4, local-first, keyboard-centric
- **Respect user time**: Timer-driven, group execution, focus through time budget

## Ways to Contribute

### 1. Code Contributions

**Before Starting**
- Check `docs/COMMUNITY_STRATEGY.md` for accepted/rejected features
- Open an issue/discussion if unsure (saves wasted effort)
- Read `docs/ARCHITECTURE.md` to understand system design

**Development Setup**
```bash
git clone https://github.com/matiasz8/pulseTask.git
cd pulseTask
make venv && make sync && make doctor-gtk
```

**Local Development**
```bash
make run           # Start app
make test          # Run tests (watch for failures)
make lint          # Lint with ruff
make typecheck     # Type check with mypy
```

**Common Tasks**
```bash
# Run specific test
uv run pytest tests/test_group_service.py::test_group_creation -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Format code (ruff will auto-suggest)
uv run ruff check --fix .
```

### 2. Documentation

- **API**: Update `docs/API.md` if services change
- **Architecture**: Update `docs/ARCHITECTURE.md` for structural changes
- **User Guide**: Create `docs/GUIDE_*.md` for workflows
- **README**: High-level overview stays minimal
- **Accessibility**: Update `docs/ACCESSIBILITY_CHECKLIST.md` if UI changes

### 3. Bug Reports

**Template**
```
### System
- OS: Ubuntu 24.04 LTS
- Python: 3.12.3
- PulseTask: v0.2.0

### Reproduction Steps
1. Create a group with 3 tasks
2. Start execution
3. Wait 5 seconds
4. Pause

### Expected Behavior
Pause button should freeze timer

### Actual Behavior
Timer continues

### Logs
```bash
make run 2>&1 | tail -20
```
```

### 4. Feature Discussions

**Before requesting features**, read `docs/COMMUNITY_STRATEGY.md`.

**Features aligned with philosophy** (we'd consider):
- GNOME Shell integration (native citizen)
- Better statistics visualization (clarity)
- Custom keyboard shortcuts (power user ergonomics)
- Import/export workflows (data ownership)
- Accessibility improvements (WCAG AA → AAA)

**Features misaligned** (we'd decline):
- Cloud sync (contradicts local-first)
- Team collaboration (scope creep)
- Mobile app (desktop-only focus)
- AI productivity coaching (marketing noise)
- "More widgets" (constraint is our strength)

**The Ask:** If suggesting a feature, explain how it improves **execution clarity**, not just convenience.

### 5. Testing

We maintain 85%+ coverage. Help us test:
- Ubuntu 22.04 LTS, 24.04 LTS, 24.10
- GTK4/libadwaita compatibility
- Different window managers (Wayland, X11)
- Accessibility: keyboard + screen reader

### 6. Community Building

- Share PulseTask in Linux communities
- Write about your workflow using PulseTask
- Contribute testimonials (we'll feature them)
- Help moderate GitHub Discussions

## Workflow

### Branches

- `main`: Production only (v0.2.0+)
- Feature: `feat/short-name` from `main`
- Bug: `fix/short-name` from `main`
- Docs: `docs/short-name` from `main`

**Example**
```bash
git checkout -b feat/stats-export-csv
# Make changes
make test && make lint && make typecheck  # All pass
git add -A
git commit -m "feat(stats): add CSV export for daily metrics"
git push origin feat/stats-export-csv
# Open PR on GitHub
```

### Commit Messages

**Format**: `type(scope): description`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Test coverage
- `refactor`: Code reorganization (no behavior change)
- `chore`: Dependencies, CI, tooling
- `perf`: Performance improvement

**Examples**:
```
feat(group): add skip-remaining-tasks method
fix(ui): resolve focus indicator on timer display
docs(api): clarify GroupService initialization
test(stats): add weekly aggregation tests
perf(db): add index on task_groups.completed_at
chore(deps): update mypy to 2.1.0
```

### Pull Requests

**Before Opening**:
1. [ ] All tests pass: `make test`
2. [ ] No lint errors: `make lint`
3. [ ] Type check passes: `make typecheck`
4. [ ] Commit messages follow format above
5. [ ] PR title is descriptive
6. [ ] Description explains _why_, not just _what_

**PR Template** (auto-filled):
```markdown
## What
Briefly describe the change.

## Why
Why is this change needed? What problem does it solve?

## Testing
How did you test this? Include reproduction steps or test output.

## Checklist
- [ ] Tests pass
- [ ] Lint passes
- [ ] Type checking passes
- [ ] Docs updated (if needed)
```

**Example**
```
## What
Add CSV export for daily statistics

## Why
Users want to analyze PulseTask data in spreadsheets without manual copying.

## Testing
Ran stats service with 10 completed groups, exported CSV. Verified:
- Headers correct
- All metrics present
- Data accuracy (spot-checked completion rates)

## Checklist
- [x] Tests pass (3 new tests for CSV export)
- [x] Lint passes
- [x] Type checking passes
- [x] Docs updated (API.md)
```

## Code Style

### Python

**Type hints everywhere**:
```python
def create_group(
    name: str,
    time_budget_seconds: int,
    tasks: list[TaskSpec]
) -> TaskGroup:
    """Create a task group with time budget."""
```

**Docstrings for public APIs**:
```python
def pause_group(self, group_id: str) -> None:
    """Pause execution, preserving elapsed time and task order."""
```

**Line length**: 100 chars (enforced by ruff)

**Test naming**: `test_<what>_<when>_<expect>`
```python
def test_advance_to_next_task_when_current_complete_should_skip():
    # test logic
```

### UI (GTK4)

**Compose components** (no god objects):
```python
class TimerDisplay(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.label = Gtk.Label(label="00:00")
        self.append(self.label)

class GroupExecutionWindow(Gtk.ApplicationWindow):
    def __init__(self, service, group):
        super().__init__()
        self.timer = TimerDisplay()
        self.append(self.timer)
```

**CSS for styling**, not inline:
```python
# Good
self.add_css_class("timer-display")

# Avoid
label.set_markup("<big><b>%s</b></big>" % time)
```

**Keyboard accessibility** (Tab through all controls):
```python
button.set_can_focus(True)
entry.set_has_focus(True)
# Focus flows logically
```

**Focus indicators** (always visible):
```css
*:focus-visible {
    outline: 3px solid @theme_accent_color;
    outline-offset: 2px;
}
```

### CSS

**Use theme variables**:
```css
.group-timer {
    background-color: @theme_base_color;
    color: @theme_text_color;
}
```

**Accessibility media queries**:
```css
@media (prefers-contrast) {
    .group-timer {
        border: 2px solid @theme_text_color;
    }
}

@media (prefers-reduced-motion) {
    * {
        animation: none !important;
    }
}
```

## Testing

### Unit Tests
```python
def test_group_creation_with_valid_tasks():
    service = GroupService(Database(":memory:"))
    group = service.create_group(
        name="Sprint",
        time_budget_seconds=600,
        tasks=[TaskSpec(name="Task 1", estimated_duration=10)]
    )
    assert group.status == GroupStatus.IDLE
    assert group.tasks_count == 1
```

### Integration Tests
```python
def test_full_execution_workflow():
    service = GroupService(Database(":memory:"))
    group = service.create_group(...)
    service.start_group(group.id)
    service.advance_to_next_task(group.id)
    service.pause_group(group.id)
    service.resume_group(group.id)
    service.complete_group(group.id)
    # Verify final state
```

### Coverage
```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Ground Rules

- **English first**: All code, commits, docs, issues in English
- **Small, focused PRs**: Keep changes <500 lines (easier to review)
- **One problem per issue**: Don't bundle unrelated fixes
- **Respect constraints**: "No" sometimes means "not aligned with philosophy"
- **Be respectful**: Disagreement is okay, rudeness isn't

## Issues and Discussions

- **Bugs**: Use GitHub Issues with reproduction steps
- **Features**: Use GitHub Discussions (not Issues) to discuss first
- **Usage questions**: Use GitHub Discussions
- **General feedback**: Use GitHub Discussions

Maintainers follow `docs/ISSUE_TRIAGE.md` for triage process.

## Definition of Done

✅ **Before merging, PR must have:**

- [ ] Tests added/updated and passing (`make test`)
- [ ] No lint errors (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Commits follow `type(scope): description` format
- [ ] Documentation updated (if behavior changed)
- [ ] No regressions in group execution or timer semantics
- [ ] Accessibility maintained (keyboard navigation, focus indicators)

## Recognition

Contributors are:
- Listed in `CONTRIBUTORS.md` (after first merged PR)
- Thanked in release notes
- Featured in community highlights

---

**Questions?**
1. Check `docs/` folder (API, Architecture, Accessibility)
2. Read existing issues/PRs (your question might be answered)
3. Open a GitHub Discussion
4. Join us on GitHub

**Thank you for making PulseTask better!** 🐧
