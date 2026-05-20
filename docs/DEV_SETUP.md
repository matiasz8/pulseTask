# Development Setup

## Prerequisites

- Python 3.12+
- uv
- make

## Local Bootstrap

```bash
make venv
make sync
make ci
```

## Daily Commands

```bash
make test
make lint
make typecheck
make run
```

## Notes

- Use uv as the default Python toolchain for dependency resolution and command execution.
- Keep all contributions in English (code comments, docs, issue/PR text).
