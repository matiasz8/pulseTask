# Contributing to PulseTask

Thanks for helping improve PulseTask.

## Ground Rules

- Use English for all code, docs, comments, issues, and pull requests.
- Keep pull requests focused and small.
- Add tests for behavior changes.
- Be respectful and constructive.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Branching

- Create feature branches from `main`.
- Naming examples:
  - `feat/timer-pause-resume`
  - `fix/sqlite-state-transition`
  - `docs/contributing-guide`

## Commit Messages

Use concise English messages.

Examples:

- `feat(timer): add absolute-target countdown recovery`
- `fix(persistence): persist running task state atomically`
- `docs(readme): clarify local development setup`

## Pull Requests

Before opening a PR:

1. Run tests locally.
2. Run lint and type checks.
3. Update docs if behavior changed.
4. Fill the PR template completely.

## Issues and Discussions

- Use the GitHub Issue Forms for bug reports and feature requests.
- Keep one problem/request per issue.
- Include reproduction details and environment data for bugs.
- Use GitHub Discussions for usage questions and support.
- Maintainers follow the triage process in `docs/ISSUE_TRIAGE.md`.

## Definition of Done

- Tests added/updated and passing
- CI green
- English-first requirement respected
- No regressions in task states or timer semantics
