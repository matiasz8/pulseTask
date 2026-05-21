# Issue Triage Guide

This guide defines how maintainers triage new issues for consistent open-source collaboration.

## Triage SLA

- Acknowledge new issues within 3 business days.
- Add or adjust labels during first triage pass.
- Close duplicates with a pointer to the canonical issue.

## Required Labels

- `needs-triage`: default label for newly opened issues.
- `bug`: reproducible defect.
- `enhancement`: accepted feature request.
- `question`: usage/help request (prefer GitHub Discussions).
- `blocked`: cannot proceed without external dependency.

## Triage Steps

1. Verify template completeness (description, repro steps, environment).
2. Reproduce bug reports on current `main` when possible.
3. Confirm issue type and relabel if needed.
4. Link duplicates, related PRs, and related roadmap items.
5. Add a short next action comment for transparency.

## Hygiene Rules

- Keep one problem per issue.
- Prefer objective acceptance criteria for feature requests.
- Move support questions to Discussions when no code change is needed.
- Close stale issues only with explicit rationale.
