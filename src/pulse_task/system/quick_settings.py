"""Quick Settings widget for PulseTask status and controls."""
# mypy: ignore-errors

from __future__ import annotations

import logging
from typing import Any, cast

from pulse_task.core.group_service import GroupService
from pulse_task.dbus.status import StatusInterface, StatusSnapshot

logger = logging.getLogger(__name__)

try:
    import gi

    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gdk, Gio, GLib, Gtk
except (ImportError, ValueError):  # pragma: no cover - GTK unavailable in headless checks
    Adw = cast(Any, None)
    Gdk = cast(Any, None)
    Gio = cast(Any, None)
    GLib = cast(Any, None)
    Gtk = cast(Any, None)


class QuickSettingsWidget(Adw.ActionRow):
    """Compact Libadwaita widget for active PulseTask status."""

    _STYLE_PROVIDER: Any | None = None

    def __init__(
        self,
        service: GroupService,
        status_interface: StatusInterface,
        settings: Any | None = None,
    ) -> None:
        """Initialize the widget.

        Args:
            service: Group service used for pause and resume operations.
            status_interface: Status broadcaster used for real-time updates.
            settings: Optional Gio.Settings-compatible object.
        """
        if Adw is None or Gtk is None:
            raise RuntimeError("GTK4/Libadwaita is required for QuickSettingsWidget")

        super().__init__()
        self.service = service
        self.status_interface = status_interface
        self.settings = settings or self._load_settings()
        self._signal_ids: list[int] = []
        self._settings_handler: int | None = None
        self._timer_id: int | None = None
        self.position = self._get_int("last-quick-settings-position", 0)

        self.set_title("PulseTask")
        self.set_subtitle("No active group")
        self.add_prefix(Gtk.Image.new_from_icon_name("preferences-system-time-symbolic"))

        suffix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.status_label = Gtk.Label(label="Idle")
        self.status_label.add_css_class("quick-settings-badge")
        self.time_label = Gtk.Label(label="00:00")
        self.time_label.add_css_class("quick-settings-time")
        self.pause_button = Gtk.Button.new_from_icon_name("media-playback-start-symbolic")
        self.pause_button.set_tooltip_text("Resume PulseTask")
        self.pause_button.connect("clicked", self._on_pause_clicked)
        suffix.append(self.status_label)
        suffix.append(self.time_label)
        suffix.append(self.pause_button)
        self.add_suffix(suffix)
        self.set_activatable_widget(self.pause_button)

        self._install_styles()
        self._connect_status_signals()
        self._connect_settings_signal()
        self._apply_visibility()
        self._apply_snapshot(self.status_interface.get_snapshot())
        self._timer_id = GLib.timeout_add_seconds(1, self._on_timer_tick)
        self.connect("destroy", self._on_destroy)

    def refresh(self) -> StatusSnapshot:
        """Refresh the widget from the latest execution snapshot."""
        snapshot = self.status_interface.refresh()
        self._apply_snapshot(snapshot)
        return snapshot

    def remember_position(self, position: int) -> None:
        """Persist the last shell placement used for the widget."""
        self.position = position
        if self.settings is not None and hasattr(self.settings, "set_int"):
            self.settings.set_int("last-quick-settings-position", position)

    def _connect_status_signals(self) -> None:
        for signal_name in ("GroupStatusChanged", "TimeUpdated", "TaskChanged"):
            handler_id = self.status_interface.connect(signal_name, self._apply_snapshot)
            self._signal_ids.append(handler_id)

    def _connect_settings_signal(self) -> None:
        if self.settings is not None and hasattr(self.settings, "connect"):
            self._settings_handler = self.settings.connect(
                "changed::show-quick-settings",
                lambda *_args: self._apply_visibility(),
            )

    def _apply_snapshot(self, snapshot: StatusSnapshot) -> None:
        self.set_subtitle(snapshot.group_name or "No active group")
        self.status_label.set_label(snapshot.status)
        self._set_badge_style(snapshot.status)
        self.time_label.set_label(self._format_seconds(snapshot.time_remaining))
        self.pause_button.set_sensitive(snapshot.group_id is not None)
        icon_name = (
            "media-playback-start-symbolic"
            if snapshot.is_paused or snapshot.group_id is None
            else "media-playback-pause-symbolic"
        )
        tooltip = "Resume PulseTask" if snapshot.is_paused else "Pause PulseTask"
        self.pause_button.set_icon_name(icon_name)
        self.pause_button.set_tooltip_text(tooltip)

    def _set_badge_style(self, status: str) -> None:
        for css_class in ("status-running", "status-paused", "status-idle"):
            self.status_label.remove_css_class(css_class)
        self.status_label.add_css_class(
            {
                "Running": "status-running",
                "Paused": "status-paused",
                "Idle": "status-idle",
            }.get(status, "status-idle")
        )

    def _apply_visibility(self) -> None:
        self.set_visible(self._get_boolean("show-quick-settings", True))

    def _on_pause_clicked(self, _button: Any) -> None:
        try:
            self.status_interface.toggle_paused()
        except Exception:  # pragma: no cover - defensive GTK callback guard
            logger.exception("Quick Settings pause toggle failed")

    def _on_timer_tick(self) -> bool:
        self.refresh()
        return True

    def _on_destroy(self, _widget: Any) -> None:
        for handler_id in self._signal_ids:
            self.status_interface.disconnect(handler_id)
        self._signal_ids.clear()
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        if self.settings is not None and self._settings_handler is not None:
            self.settings.disconnect(self._settings_handler)
            self._settings_handler = None

    def _load_settings(self) -> Any | None:
        if Gio is None:
            return None
        try:
            return Gio.Settings.new("org.gnome.Pulse")
        except Exception:
            logger.debug("GSettings unavailable for Quick Settings", exc_info=True)
            return None

    def _get_boolean(self, key: str, default: bool) -> bool:
        if self.settings is None or not hasattr(self.settings, "get_boolean"):
            return default
        return bool(self.settings.get_boolean(key))

    def _get_int(self, key: str, default: int) -> int:
        if self.settings is None or not hasattr(self.settings, "get_int"):
            return default
        return int(self.settings.get_int(key))

    def _install_styles(self) -> None:
        if QuickSettingsWidget._STYLE_PROVIDER is not None:
            return
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b".quick-settings-badge { border-radius: 999px; padding: 4px 8px; }"
            b".quick-settings-time { font-family: monospace; font-weight: 700; }"
            b".status-running { background-color: @accent_bg_color; color: @accent_fg_color; }"
            b".status-paused { background-color: @warning_bg_color; color: @warning_fg_color; }"
            b".status-idle { background-color: @dim_bg_color; color: @dim_label_fg_color; }"
        )
        display = self.get_display()
        if display is None and Gdk is not None:
            display = Gdk.Display.get_default()
        if display is None:
            return
        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        QuickSettingsWidget._STYLE_PROVIDER = provider

    def _format_seconds(self, seconds_remaining: int) -> str:
        minutes, seconds = divmod(max(0, seconds_remaining), 60)
        return f"{minutes:02d}:{seconds:02d}"
