from __future__ import annotations

# mypy: ignore-errors
from dataclasses import dataclass

from pulse_task.core.task import Task, TaskStatus


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


def _choose_toggle_label(tasks: list[Task]) -> str:
    running = next((task for task in tasks if task.status == TaskStatus.RUNNING), None)
    if running is not None:
        return "Pause active"

    paused = next((task for task in tasks if task.status == TaskStatus.PAUSED), None)
    if paused is not None:
        return "Resume next"

    pending = next((task for task in tasks if task.status == TaskStatus.PENDING), None)
    if pending is not None:
        return "Start next"

    return "Start/Pause"


class TrayController:
    def __init__(
        self,
        on_open: callable,
        on_toggle: callable,
        on_reset: callable,
        on_quit: callable,
        format_seconds: callable,
    ) -> None:
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import AyatanaAppIndicator3 as AppIndicator3
        from gi.repository import Gtk

        self._on_open = on_open
        self._on_toggle = on_toggle
        self._on_reset = on_reset
        self._on_quit = on_quit
        self._format_seconds = format_seconds

        self._indicator = AppIndicator3.Indicator.new(
            "pulsetask-indicator",
            "appointment-soon",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_title("PulseTask")

        menu = Gtk.Menu()

        self._open_item = Gtk.MenuItem(label="Open PulseTask")
        self._open_item.connect("activate", lambda *_: self._on_open())
        menu.append(self._open_item)

        self._toggle_item = Gtk.MenuItem(label="Start/Pause")
        self._toggle_item.connect("activate", lambda *_: self._on_toggle())
        menu.append(self._toggle_item)

        self._reset_item = Gtk.MenuItem(label="Reset active")
        self._reset_item.connect("activate", lambda *_: self._on_reset())
        menu.append(self._reset_item)

        menu.append(Gtk.SeparatorMenuItem())

        self._quit_item = Gtk.MenuItem(label="Quit")
        self._quit_item.connect("activate", lambda *_: self._on_quit())
        menu.append(self._quit_item)

        menu.show_all()
        self._indicator.set_menu(menu)
        self._set_label("--:--")

    def _set_label(self, label: str) -> None:
        if hasattr(self._indicator, "set_label"):
            self._indicator.set_label(label, "")

    def update(self, tasks: list[Task]) -> None:
        running = next((task for task in tasks if task.status == TaskStatus.RUNNING), None)
        if running is not None:
            self._set_label(self._format_seconds(running.remaining_seconds))
            self._reset_item.set_sensitive(True)
        else:
            self._set_label("--:--")
            has_candidate = any(
                task.status in {TaskStatus.PENDING, TaskStatus.PAUSED} for task in tasks
            )
            self._reset_item.set_sensitive(has_candidate)

        self._toggle_item.set_label(_choose_toggle_label(tasks))

    def shutdown(self) -> None:
        self._indicator.set_status(0)


def build_tray_controller(
    on_open: callable,
    on_toggle: callable,
    on_reset: callable,
    on_quit: callable,
    format_seconds: callable,
) -> TrayController | None:
    caps = detect_tray_capabilities()
    if not caps.available:
        return None
    try:
        return TrayController(
            on_open=on_open,
            on_toggle=on_toggle,
            on_reset=on_reset,
            on_quit=on_quit,
            format_seconds=format_seconds,
        )
    except Exception:
        return None
