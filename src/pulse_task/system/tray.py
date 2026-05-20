from __future__ import annotations

# mypy: ignore-errors
from dataclasses import dataclass


@dataclass(slots=True)
class TrayCapabilities:
    available: bool
    reason: str = ""


def detect_tray_capabilities() -> TrayCapabilities:
    """Detect whether AppIndicator-style tray support is available.

    This is a non-fatal capability check used to keep behavior stable on
    Wayland/GNOME setups where tray support may be missing.
    """
    try:
        import gi

        gi.require_version("AyatanaAppIndicator3", "0.1")
        return TrayCapabilities(available=True)
    except Exception as exc:  # pragma: no cover - environment dependent
        return TrayCapabilities(available=False, reason=str(exc))
