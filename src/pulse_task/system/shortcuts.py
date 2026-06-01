"""Global GNOME keyboard shortcuts for PulseTask."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from typing import Any, cast

logger = logging.getLogger(__name__)

try:
    import gi  # type: ignore[import-untyped]

    gi.require_version("Gio", "2.0")
    gi.require_version("GLib", "2.0")
    from gi.repository import Gio, GLib  # type: ignore[import-untyped]
except (ImportError, ValueError):  # pragma: no cover - depends on desktop runtime
    Gio = cast(Any, None)
    GLib = cast(Any, None)

DEFAULT_SHORTCUTS: dict[str, str] = {
    "pause-resume": "<Super>alt+p",
    "new-task": "<Super>alt+n",
    "show-stats": "<Super>alt+s",
    "bring-window": "<Super>alt+t",
}
SHORTCUT_KEYS: dict[str, str] = {
    "pause-resume": "shortcut-pause-resume",
    "new-task": "shortcut-new-task",
    "show-stats": "shortcut-show-stats",
    "bring-window": "shortcut-bring-window",
}
_MODIFIERS = {"super", "alt", "shift", "primary", "ctrl", "control"}


class GlobalShortcuts:
    """Register and handle GNOME Shell global accelerators."""

    def __init__(
        self,
        *,
        settings: Any | None = None,
        bus: Any | None = None,
        on_pause_resume: Callable[[], None] | None = None,
        on_new_task: Callable[[], None] | None = None,
        on_show_stats: Callable[[], None] | None = None,
        on_bring_window: Callable[[], None] | None = None,
    ) -> None:
        self.settings = settings or self._load_settings()
        self.bus = bus or self._load_bus()
        self._handlers = {
            "pause-resume": on_pause_resume,
            "new-task": on_new_task,
            "show-stats": on_show_stats,
            "bring-window": on_bring_window,
        }
        self._grabbed: dict[int, str] = {}
        self._subscription_id: int | None = None

    @staticmethod
    def parse_shortcut(accelerator: str) -> tuple[str, ...] | None:
        """Return normalized tokens for a GTK accelerator string."""
        if accelerator.endswith("+"):
            return None
        normalized = re.sub(r"<([^>]+)>", lambda match: f"{match.group(1)}+", accelerator)
        tokens = [token.strip().lower() for token in normalized.split("+") if token.strip()]
        if not tokens or any(not re.fullmatch(r"[a-z0-9,]+", token) for token in tokens):
            return None
        if tokens[-1] in _MODIFIERS or any(token not in _MODIFIERS for token in tokens[:-1]):
            return None
        return tuple(tokens)

    def register_shortcuts(self) -> bool:
        """Register configured accelerators with GNOME Shell when available."""
        self.unregister_shortcuts()
        if not self._enabled() or self.bus is None or Gio is None or GLib is None:
            logger.info("Global shortcuts unavailable or disabled")
            return False
        try:
            self._subscription_id = self.bus.signal_subscribe(
                "org.gnome.Shell",
                "org.gnome.Shell",
                "AcceleratorActivated",
                "/org/gnome/Shell",
                None,
                Gio.DBusSignalFlags.NONE,
                self._on_shortcut_activated,
            )
            for shortcut_id, default in DEFAULT_SHORTCUTS.items():
                accelerator = self._shortcut_value(shortcut_id, default)
                result = self.bus.call_sync(
                    "org.gnome.Shell",
                    "/org/gnome/Shell",
                    "org.gnome.Shell",
                    "GrabAccelerator",
                    GLib.Variant("(su)", (accelerator, 0)),
                    GLib.VariantType("(u)"),
                    Gio.DBusCallFlags.NONE,
                    -1,
                    None,
                )
                action_id = int(result.unpack()[0])
                if action_id == 0:
                    logger.info("Global shortcut already claimed: %s", accelerator)
                    continue
                self._grabbed[action_id] = shortcut_id
                logger.debug("Registered %s as action %s", accelerator, action_id)
        except Exception:
            logger.warning("Unable to register GNOME global shortcuts", exc_info=True)
            self.unregister_shortcuts()
        return bool(self._grabbed)

    def unregister_shortcuts(self) -> None:
        """Release previously registered accelerators."""
        if self.bus is not None and Gio is not None and GLib is not None:
            for action_id in tuple(self._grabbed):
                try:
                    self.bus.call_sync(
                        "org.gnome.Shell",
                        "/org/gnome/Shell",
                        "org.gnome.Shell",
                        "UngrabAccelerator",
                        GLib.Variant("(u)", (action_id,)),
                        GLib.VariantType("(b)"),
                        Gio.DBusCallFlags.NONE,
                        -1,
                        None,
                    )
                except Exception:
                    logger.debug("Failed to ungrab shortcut %s", action_id, exc_info=True)
            if self._subscription_id is not None:
                self.bus.signal_unsubscribe(self._subscription_id)
        self._grabbed.clear()
        self._subscription_id = None

    def handle_shortcut(self, shortcut_id: str) -> None:
        """Dispatch a shortcut activation to the configured callback."""
        handler = self._handlers.get(shortcut_id)
        if handler is None:
            logger.debug("No handler registered for shortcut %s", shortcut_id)
            return
        try:
            handler()
        except Exception:
            logger.exception("Shortcut handler failed for %s", shortcut_id)

    def _enabled(self) -> bool:
        return self.settings is None or bool(self.settings.get_boolean("global-shortcuts-enabled"))

    def _shortcut_value(self, shortcut_id: str, default: str) -> str:
        if self.settings is None:
            return default
        value = str(self.settings.get_string(SHORTCUT_KEYS[shortcut_id]))
        if self.parse_shortcut(value) is not None:
            return value
        logger.warning("Invalid shortcut '%s' for %s, using default", value, shortcut_id)
        return default

    def _on_shortcut_activated(self, *_args: object) -> None:
        parameters = cast(Any, _args[-1])
        payload = parameters.unpack() if parameters is not None else ()
        if not payload:
            return
        shortcut_id = self._grabbed.get(int(payload[0]))
        if shortcut_id is not None:
            self.handle_shortcut(shortcut_id)

    def _load_settings(self) -> Any | None:
        if Gio is None:
            return None
        try:
            return Gio.Settings.new("org.gnome.Pulse")
        except Exception:
            logger.debug("GSettings unavailable for global shortcuts", exc_info=True)
            return None

    def _load_bus(self) -> Any | None:
        if Gio is None:
            return None
        try:
            return Gio.bus_get_sync(Gio.BusType.SESSION, None)
        except Exception:
            logger.debug("D-Bus session bus unavailable for global shortcuts", exc_info=True)
            return None
