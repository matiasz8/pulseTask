# Development Setup

## Prerequisites

- Python 3.12+
- uv
- make

## Local Bootstrap

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin libcanberra-gtk3-module
make venv
make sync
make doctor-gtk
make ci
```

If you installed GTK dependencies after creating the virtual environment, recreate it:

```bash
rm -rf .venv
make venv
make sync
make doctor-gtk
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
