"""Settings window for PulseTask."""
# mypy: ignore-errors

from __future__ import annotations

from pathlib import Path

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Adw", "1")  # noqa: E402

from gi.repository import Adw, Gio, Gtk  # noqa: E402 # type: ignore[import-untyped]

SCHEMA_ID = "org.gnome.Pulse"
WEEK_START_OPTIONS: tuple[str, str] = ("Monday", "Sunday")
REQUIRED_KEYS: tuple[str, ...] = (
    "dark-mode",
    "week-start",
    "auto-start-next",
    "show-time-in-title",
    "pause-on-blur",
    "notifications-enabled",
    "expiration-warnings",
    "warning-threshold",
)


class SettingsWindow(Adw.PreferencesWindow):
    """Preferences window backed by GSettings."""

    def __init__(
        self,
        app: Gtk.Application,
        parent: Gtk.Window | None = None,
    ) -> None:
        """Initialize the settings window."""
        super().__init__(application=app)
        self.settings = Gio.Settings.new(SCHEMA_ID)
        self.style_manager = Adw.StyleManager.get_default()

        self._validate_required_keys()
        self._load_styles()

        if parent is not None and hasattr(self, "set_transient_for"):
            self.set_transient_for(parent)

        self.set_modal(True)
        self.set_title("Settings")
        self.set_default_size(720, 560)
        self.set_search_enabled(False)

        self.add(self._build_general_page())
        self.add(self._build_focus_page())
        self.add(self._build_notifications_page())

        self._bind_gsettings()
        self._apply_dark_mode(self.settings.get_boolean("dark-mode"))
        self._sync_week_start_from_settings()
        self._sync_warning_threshold_from_settings()
        self._sync_notification_rows()

    def _validate_required_keys(self) -> None:
        """Ensure the expected settings keys are available in the schema."""
        available_keys = set(self.settings.list_keys())
        missing_keys = [key for key in REQUIRED_KEYS if key not in available_keys]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise ValueError(
                f"Missing GSettings keys in {SCHEMA_ID}: {missing}"
            )

    def _load_styles(self) -> None:
        """Load optional CSS for the settings window."""
        css_path = Path(__file__).with_name("styles_settings.css")
        if not css_path.exists() or css_path.stat().st_size == 0:
            return

        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_path))
        display = self.get_display()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def _build_general_page(self) -> Adw.PreferencesPage:
        """Build the general settings page."""
        page = Adw.PreferencesPage()
        page.set_title("General")
        page.set_icon_name("emblem-system-symbolic")

        appearance_group = Adw.PreferencesGroup()
        appearance_group.set_title("Appearance")
        self.dark_mode_row = self._create_switch_row("Dark mode")
        appearance_group.add(self.dark_mode_row)

        calendar_group = Adw.PreferencesGroup()
        calendar_group.set_title("Calendar")
        self.week_start_row = Adw.ComboRow()
        self.week_start_row.set_title("Week starts on")
        self.week_start_row.set_model(Gtk.StringList.new(list(WEEK_START_OPTIONS)))
        calendar_group.add(self.week_start_row)

        page.add(appearance_group)
        page.add(calendar_group)
        return page

    def _build_focus_page(self) -> Adw.PreferencesPage:
        """Build the focus settings page."""
        page = Adw.PreferencesPage()
        page.set_title("Focus")
        page.set_icon_name("focus-symbolic")

        behavior_group = Adw.PreferencesGroup()
        behavior_group.set_title("Focus Behavior")

        self.auto_start_row = self._create_switch_row("Auto-start next task")
        self.show_time_in_title_row = self._create_switch_row(
            "Show remaining time in title"
        )
        self.pause_on_blur_row = self._create_switch_row("Pause on window blur")

        behavior_group.add(self.auto_start_row)
        behavior_group.add(self.show_time_in_title_row)
        behavior_group.add(self.pause_on_blur_row)

        page.add(behavior_group)
        return page

    def _build_notifications_page(self) -> Adw.PreferencesPage:
        """Build the notifications settings page."""
        page = Adw.PreferencesPage()
        page.set_title("Notifications")
        page.set_icon_name("notifications-symbolic")

        notifications_group = Adw.PreferencesGroup()
        notifications_group.set_title("Desktop Notifications")

        self.notifications_enabled_row = self._create_switch_row(
            "Show desktop notifications"
        )
        self.expiration_warnings_row = self._create_switch_row("Expiration warnings")
        self.warning_threshold_row = Adw.SpinRow.new_with_range(1, 60, 1)
        self.warning_threshold_row.set_title("Warning threshold")
        self.warning_threshold_row.set_subtitle("Minutes before a task expires")
        self.warning_threshold_row.set_numeric(True)
        self.warning_threshold_row.set_digits(0)

        notifications_group.add(self.notifications_enabled_row)
        notifications_group.add(self.expiration_warnings_row)
        notifications_group.add(self.warning_threshold_row)

        page.add(notifications_group)
        return page

    def _create_switch_row(self, title: str) -> Adw.SwitchRow:
        """Create a standard switch row."""
        row = Adw.SwitchRow()
        row.set_title(title)
        return row

    def _bind_gsettings(self) -> None:
        """Bind GSettings keys to the window controls."""
        self.settings.bind(
            "dark-mode",
            self.dark_mode_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "auto-start-next",
            self.auto_start_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "show-time-in-title",
            self.show_time_in_title_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "pause-on-blur",
            self.pause_on_blur_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "notifications-enabled",
            self.notifications_enabled_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.settings.bind(
            "expiration-warnings",
            self.expiration_warnings_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )

        self.dark_mode_row.connect("notify::active", self._on_dark_mode_toggled)
        self.week_start_row.connect("notify::selected", self._on_week_start_selected)
        self.warning_threshold_row.connect(
            "notify::value",
            self._on_warning_threshold_changed,
        )

        self.settings.connect("changed::dark-mode", self._on_dark_mode_changed)
        self.settings.connect("changed::week-start", self._sync_week_start_from_settings)
        self.settings.connect(
            "changed::warning-threshold",
            self._sync_warning_threshold_from_settings,
        )
        self.settings.connect(
            "changed::notifications-enabled",
            self._sync_notification_rows,
        )
        self.settings.connect(
            "changed::expiration-warnings",
            self._sync_notification_rows,
        )

    def _on_dark_mode_toggled(self, row: Adw.SwitchRow, _pspec: object) -> None:
        """Apply dark mode as soon as the toggle changes."""
        self._apply_dark_mode(row.get_active())

    def _on_dark_mode_changed(self, _settings: Gio.Settings, _key: str) -> None:
        """Keep the style manager in sync with the stored dark mode value."""
        self._apply_dark_mode(self.settings.get_boolean("dark-mode"))

    def _apply_dark_mode(self, enabled: bool) -> None:
        """Apply the selected color scheme immediately."""
        if enabled:
            self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            return
        self.style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def _on_week_start_selected(self, row: Adw.ComboRow, _pspec: object) -> None:
        """Store the selected week start value."""
        selected = self._selected_week_start(row.get_selected())
        if selected != self.settings.get_string("week-start"):
            self.settings.set_string("week-start", selected)

    def _sync_week_start_from_settings(self, *_args: object) -> None:
        """Refresh the week start row from GSettings."""
        value = self.settings.get_string("week-start")
        try:
            index = WEEK_START_OPTIONS.index(value)
        except ValueError:
            index = 0
        if self.week_start_row.get_selected() != index:
            self.week_start_row.set_selected(index)

    def _selected_week_start(self, index: int) -> str:
        """Return the string value for a combo row index."""
        if 0 <= index < len(WEEK_START_OPTIONS):
            return WEEK_START_OPTIONS[index]
        return WEEK_START_OPTIONS[0]

    def _on_warning_threshold_changed(self, row: Adw.SpinRow, _pspec: object) -> None:
        """Store the warning threshold in minutes."""
        value = int(row.get_value())
        if value != self.settings.get_int("warning-threshold"):
            self.settings.set_int("warning-threshold", value)

    def _sync_warning_threshold_from_settings(self, *_args: object) -> None:
        """Refresh the warning threshold row from GSettings."""
        value = self.settings.get_int("warning-threshold")
        if int(self.warning_threshold_row.get_value()) != value:
            self.warning_threshold_row.set_value(float(value))

    def _sync_notification_rows(self, *_args: object) -> None:
        """Enable or disable dependent notification controls."""
        notifications_enabled = self.settings.get_boolean("notifications-enabled")
        expiration_warnings = self.settings.get_boolean("expiration-warnings")

        self.expiration_warnings_row.set_sensitive(notifications_enabled)
        self.warning_threshold_row.set_sensitive(notifications_enabled and expiration_warnings)
