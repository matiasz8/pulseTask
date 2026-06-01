"""Desktop notification manager using the freedesktop.org D-Bus interface."""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from typing import Any, Protocol, cast

try:
    from gi.repository import Gio, GLib  # type: ignore[import-untyped]
except (ImportError, ValueError):
    Gio = cast(Any, None)
    GLib = cast(Any, None)

logger = logging.getLogger(__name__)
ActionCallback = Callable[[], None]


class SettingsProtocol(Protocol):
    """Minimal settings contract used by :class:`NotificationManager`."""

    def get_boolean(self, key: str) -> bool:
        """Return a boolean setting value."""

    def get_int(self, key: str) -> int:
        """Return an integer setting value."""


class NotificationManager:
    """Send actionable desktop notifications over D-Bus."""

    BUS_NAME = "org.freedesktop.Notifications"
    OBJECT_PATH = "/org/freedesktop/Notifications"
    INTERFACE = "org.freedesktop.Notifications"
    APP_NAME = "PulseTask"
    DESKTOP_ENTRY = "org.gnome.Pulse"

    def __init__(
        self,
        settings: SettingsProtocol | None = None,
        bus: Any | None = None,
    ) -> None:
        """Initialize the notification manager.

        Args:
            settings: Optional GSettings-compatible object.
            bus: Optional injected D-Bus connection for tests.
        """
        self.settings = settings if settings is not None else self._load_settings()
        self._bus = bus
        self._signals_connected = False
        self._action_handlers: dict[int, dict[str, ActionCallback]] = {}
        self._replacement_ids: dict[str, int] = {}

    @property
    def warning_threshold_seconds(self) -> int:
        """Return the warning threshold in seconds."""
        return self._get_int("expiration-warning-threshold", 300)

    def send_task_expired(
        self,
        task_name: str,
        *,
        on_snooze: ActionCallback | None = None,
        on_start_next: ActionCallback | None = None,
    ) -> int | None:
        """Send an expiration notification for the current task."""
        actions = ["snooze", "Snooze 5m", "start-next", "Start next", "dismiss", "Dismiss"]
        callbacks = {"snooze": on_snooze, "start-next": on_start_next}
        return self._notify(
            summary="Task expired",
            body=self._task_label(task_name),
            actions=actions,
            callbacks=callbacks,
            urgency=1,
            category="task.expired",
            timeout_ms=self._get_int("notification-timeout", 10000),
            replace_key="task-expired",
        )

    def send_time_warning(
        self,
        task_name: str,
        seconds_remaining: int,
        *,
        on_extend: ActionCallback | None = None,
    ) -> int | None:
        """Send a warning notification before the timer expires."""
        minutes_remaining = max(1, math.ceil(seconds_remaining / 60))
        summary = f"{minutes_remaining} minute remaining"
        if minutes_remaining != 1:
            summary = f"{minutes_remaining} minutes remaining"
        return self._notify(
            summary=summary,
            body=self._task_label(task_name),
            actions=["extend", "Extend 5m", "continue", "Continue"],
            callbacks={"extend": on_extend},
            urgency=2,
            category="task.warning",
            timeout_ms=min(self._get_int("notification-timeout", 10000), 5000),
            replace_key="time-warning",
        )

    def send_focus_lost(
        self,
        task_name: str,
        *,
        on_resume: ActionCallback | None = None,
    ) -> int | None:
        """Send an informational notification when the window loses focus."""
        body = f"{self._task_label(task_name)} auto-paused after the window lost focus."
        return self._notify(
            summary="Window focus lost",
            body=body,
            actions=["resume", "Resume", "keep-paused", "Keep paused"],
            callbacks={"resume": on_resume},
            urgency=0,
            category="task.focus-lost",
            timeout_ms=min(self._get_int("notification-timeout", 10000), 3000),
            replace_key="focus-lost",
        )

    def _notify(
        self,
        *,
        summary: str,
        body: str,
        actions: list[str],
        callbacks: dict[str, ActionCallback | None],
        urgency: int,
        category: str,
        timeout_ms: int,
        replace_key: str,
    ) -> int | None:
        """Send a notification and register action handlers."""
        if not self._notifications_enabled() or Gio is None or GLib is None:
            return None

        try:
            bus = self._ensure_bus()
            replaces_id = self._replacement_ids.get(replace_key, 0)
            parameters = GLib.Variant(
                "(susssasa{sv}i)",
                (
                    self.APP_NAME,
                    replaces_id,
                    self.DESKTOP_ENTRY,
                    summary,
                    body,
                    actions,
                    self._build_hints(urgency, category),
                    timeout_ms,
                ),
            )
            result = bus.call_sync(
                self.BUS_NAME,
                self.OBJECT_PATH,
                self.INTERFACE,
                "Notify",
                parameters,
                GLib.VariantType("(u)"),
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
            notification_id = int(result.unpack()[0])
            self._replacement_ids[replace_key] = notification_id
            self._action_handlers[notification_id] = {
                key: callback for key, callback in callbacks.items() if callback is not None
            }
            return notification_id
        except Exception:
            logger.exception("Failed to send desktop notification")
            return None

    def _ensure_bus(self) -> Any:
        """Return the session D-Bus connection."""
        if self._bus is None:
            self._bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if not self._signals_connected:
            self._bus.signal_subscribe(
                self.BUS_NAME,
                self.INTERFACE,
                "ActionInvoked",
                self.OBJECT_PATH,
                None,
                Gio.DBusSignalFlags.NONE,
                self._on_action_invoked,
            )
            self._bus.signal_subscribe(
                self.BUS_NAME,
                self.INTERFACE,
                "NotificationClosed",
                self.OBJECT_PATH,
                None,
                Gio.DBusSignalFlags.NONE,
                self._on_notification_closed,
            )
            self._signals_connected = True
        return self._bus

    def _on_action_invoked(self, *_args: Any) -> None:
        """Execute the callback registered for a notification action."""
        parameters = _args[6]
        notification_id, action_key = parameters.unpack()
        callback = self._action_handlers.pop(int(notification_id), {}).get(str(action_key))
        if callback is None:
            return
        try:
            callback()
        except Exception:
            logger.exception("Notification action callback failed")

    def _on_notification_closed(self, *_args: Any) -> None:
        """Clear handlers when a notification is dismissed."""
        notification_id = int(_args[6].unpack()[0])
        self._action_handlers.pop(notification_id, None)

    def _build_hints(self, urgency: int, category: str) -> dict[str, Any]:
        """Build freedesktop notification hints."""
        return {
            "urgency": GLib.Variant("y", urgency),
            "category": GLib.Variant("s", category),
            "desktop-entry": GLib.Variant("s", self.DESKTOP_ENTRY),
        }

    def _load_settings(self) -> SettingsProtocol | None:
        """Load PulseTask GSettings when available."""
        if Gio is None:
            return None
        try:
            return cast(SettingsProtocol, Gio.Settings.new(self.DESKTOP_ENTRY))
        except Exception:
            logger.info("GSettings unavailable for desktop notifications", exc_info=True)
            return None

    def _notifications_enabled(self) -> bool:
        """Return whether desktop notifications should be emitted."""
        if self.settings is None:
            return True
        if self._get_boolean("show-focus-mode", False):
            return False
        enabled = self._get_boolean("notification-enabled", True)
        legacy_enabled = self._get_boolean("notifications-enabled", enabled)
        return enabled and legacy_enabled

    def _get_boolean(self, key: str, default: bool) -> bool:
        """Read a boolean setting with graceful fallback."""
        if self.settings is None:
            return default
        try:
            return bool(self.settings.get_boolean(key))
        except Exception:
            return default

    def _get_int(self, key: str, default: int) -> int:
        """Read an integer setting with graceful fallback."""
        if self.settings is None:
            return default
        try:
            return int(self.settings.get_int(key))
        except Exception:
            return default

    @staticmethod
    def _task_label(task_name: str) -> str:
        """Normalize task names for notification display."""
        label = task_name.strip() or "Untitled task"
        if len(label) <= 80:
            return label
        return f"{label[:77]}..."
