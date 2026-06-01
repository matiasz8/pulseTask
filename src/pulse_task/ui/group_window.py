"""Group Task Execution Window.

Provides a dedicated interface for executing task groups with visual feedback
on timer, task progress, and control buttons.
"""
# mypy: ignore-errors

from __future__ import annotations

from datetime import UTC, datetime

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Adw", "1")  # noqa: E402

from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402 # type: ignore[import-untyped]

from pulse_task.core.group import GroupStatus, TaskGroup  # noqa: E402
from pulse_task.core.group_service import GroupService  # noqa: E402
from pulse_task.dbus.status import StatusInterface  # noqa: E402
from pulse_task.ui.settings_window import SettingsWindow  # noqa: E402


class TimerDisplay(Gtk.Label):
    """Large, readable timer display for group execution."""

    def __init__(self) -> None:
        """Initialize timer display."""
        super().__init__()
        self.set_markup('<span font="JetBrains Mono 48" weight="bold">00:00</span>')
        self.add_css_class("timer-display")


class TaskRow(Gtk.Box):
    """Single task row in the queue display."""

    def __init__(self, task_id: str, task_name: str, is_current: bool = False) -> None:
        """Initialize task row.

        Args:
            task_id: Unique task identifier
            task_name: Display name of the task
            is_current: Whether this is the currently executing task
        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_start(8)
        self.set_margin_end(8)

        # Status indicator
        self.status_label = Gtk.Label(label="○")
        self.status_label.add_css_class("task-status")
        self.append(self.status_label)

        # Task name
        name_label = Gtk.Label(label=task_name)
        name_label.set_ellipsize(3)  # End ellipsize
        self.append(name_label)

        # CSS styling
        if is_current:
            self.add_css_class("task-row-current")
            self.status_label.set_markup("●")
        else:
            self.add_css_class("task-row")


class TaskQueue(Gtk.Box):
    """List of tasks in execution order."""

    def __init__(self, tasks: list[str]) -> None:
        """Initialize task queue.

        Args:
            tasks: List of task IDs in order
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_margin_bottom(12)
        self.progress_bar.add_css_class("task-progress")
        self.append(self.progress_bar)

        # Scrollable container for tasks
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        self.append(scroll)

        # Task list box
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.list_box.add_css_class("task-queue")
        scroll.set_child(self.list_box)

        self.task_widgets: dict[str, TaskRow] = {}
        self._populate_tasks(tasks)

    def _populate_tasks(self, tasks: list[str]) -> None:
        """Populate task list."""
        for task_id in tasks:
            row = TaskRow(task_id, task_id, is_current=(task_id == tasks[0]))
            self.task_widgets[task_id] = row
            self.list_box.append(row)

    def set_current_task(self, task_id: str | None) -> None:
        """Update current task highlight."""
        for tid, widget in self.task_widgets.items():
            if tid == task_id:
                widget.add_css_class("task-row-current")
                widget.status_label.set_markup("●")
                widget.remove_css_class("task-row")
            else:
                widget.remove_css_class("task-row-current")
                widget.status_label.set_markup("○")
                widget.add_css_class("task-row")

    def set_progress(self, progress: float) -> None:
        """Update progress bar.

        Args:
            progress: Percentage (0.0 - 1.0)
        """
        self.progress_bar.set_fraction(max(0.0, min(1.0, progress)))


class ControlPanel(Gtk.Box):
    """Control buttons for group execution with improved UX."""

    def __init__(self) -> None:
        """Initialize control panel with better layout and accessibility."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_halign(Gtk.Align.CENTER)
        self.add_css_class("control-panel")

        # Play/Pause button (primary action)
        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.add_css_class("suggested-action")
        self.pause_button.add_css_class("pill-button")
        self.pause_button.set_tooltip_text("Space: Pause/Resume execution (Ctrl+P)")
        self.append(self.pause_button)

        # Skip button (secondary action)
        self.skip_button = Gtk.Button(label="Skip Task")
        self.skip_button.add_css_class("pill-button")
        self.skip_button.set_tooltip_text("Skip to next task (Ctrl+Right)")
        self.append(self.skip_button)

        # Stop button (destructive action)
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.add_css_class("pill-button")
        self.stop_button.set_tooltip_text("Stop execution and close (Ctrl+Q)")
        self.append(self.stop_button)


class StatsFooter(Gtk.Box):
    """Stats display at the bottom of the window."""

    def __init__(self) -> None:
        """Initialize stats footer."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_bottom(16)
        self.add_css_class("stats-footer")

        # Progress text
        self.progress_text = Gtk.Label(label="0 / 0 tasks completed")
        self.progress_text.set_halign(Gtk.Align.CENTER)
        self.append(self.progress_text)

        # Elapsed time
        self.elapsed_text = Gtk.Label(label="Elapsed: 0m 0s")
        self.elapsed_text.set_halign(Gtk.Align.CENTER)
        self.append(self.elapsed_text)

    def update(self, completed: int, total: int, elapsed_seconds: int) -> None:
        """Update stats display."""
        self.progress_text.set_label(f"{completed} / {total} tasks completed")

        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        self.elapsed_text.set_label(f"Elapsed: {minutes}m {seconds}s")


class GroupExecutionWindow(Gtk.ApplicationWindow):
    """Main window for group task execution."""

    def __init__(
        self,
        app: Adw.Application,
        group: TaskGroup,
        service: GroupService,
        status_interface: StatusInterface | None = None,
    ) -> None:
        """Initialize group execution window.

        Args:
            app: Adwaita application instance
            group: TaskGroup to execute
            service: GroupService for managing execution
            status_interface: Optional status broadcaster for GNOME integrations
        """
        super().__init__(application=app)
        self.group = group
        self.service = service
        self.status_interface = status_interface
        self.timer_handle: int | None = None
        self.is_paused = False
        self._has_been_active = False
        self.settings_window: SettingsWindow | None = None

        # Initialize GSettings for title countdown preference
        from gi.repository import Gio  # type: ignore[import-untyped]

        self.settings = Gio.Settings.new("org.gnome.Pulse")
        self.show_time_in_title = self.settings.get_boolean("show-time-in-title")
        self.pause_on_blur = self.settings.get_boolean("pause-on-blur")
        self.group_name = group.name

        # Listen for preference changes
        self.settings.connect("changed::show-time-in-title", self._on_show_time_in_title_changed)
        self.settings.connect("changed::pause-on-blur", self._on_pause_on_blur_changed)
        self.connect("notify::is-active", self._on_window_activity_changed)

        self._setup_actions()

        # Window setup
        self.set_title(f"Execute: {group.name}")
        self.set_default_size(600, 600)
        self.set_modal(True)
        self.add_css_class("group-window")

        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)

        header_bar = self._build_header_bar()
        vbox.append(header_bar)

        # Title
        title_label = Gtk.Label(label=group.name)
        title_label.add_css_class("title-2")
        title_label.set_margin_bottom(16)
        vbox.append(title_label)

        # Timer display
        self.timer_display = TimerDisplay()
        vbox.append(self.timer_display)

        # Task queue
        self.task_queue = TaskQueue(group.task_ids)
        vbox.append(self.task_queue)

        # Control panel
        self.controls = ControlPanel()
        vbox.append(self.controls)

        # Stats footer
        self.stats = StatsFooter()
        vbox.append(self.stats)

        # Connect signals
        self.controls.pause_button.connect("clicked", self._on_pause_clicked)
        self.controls.skip_button.connect("clicked", self._on_skip_clicked)
        self.controls.stop_button.connect("clicked", self._on_stop_clicked)

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

        self.set_child(vbox)

        # Ensure group is started
        if group.status == GroupStatus.IDLE:
            self.service.start_group_execution(group.id)
            updated = self.service.get_group(group.id)
            assert updated is not None
            self.group = updated

        self._publish_status(force=True)

        # Start timer
        self._start_timer()

    def _setup_actions(self) -> None:
        """Register window actions used by the header menu."""
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self._on_settings_activated)
        self.add_action(settings_action)

    def _setup_keyboard_shortcuts(self) -> None:
        """Register keyboard shortcuts for window actions."""
        application = self.get_application()
        if application is not None:
            application.set_accels_for_action("win.settings", ["<Primary>comma"])

    def _build_header_bar(self) -> Gtk.HeaderBar:
        """Build the header bar with the settings menu."""
        header_bar = Gtk.HeaderBar()

        menu_model = Gio.Menu()
        menu_model.append("Settings", "win.settings")

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu_model)
        menu_button.set_tooltip_text("Open window menu")
        header_bar.pack_end(menu_button)
        return header_bar

    def _on_settings_activated(
        self,
        action: Gio.SimpleAction,
        parameter: GLib.Variant | None,
    ) -> None:
        """Open the settings window from the header menu."""
        _ = action
        _ = parameter
        self._open_settings_window()

    def _open_settings_window(self) -> None:
        """Create or present the shared settings window."""
        if self.settings_window is None:
            application = self.get_application()
            if application is None:
                raise RuntimeError("Settings window requires an active application")

            self.settings_window = SettingsWindow(application, parent=self)
            self.settings_window.connect("close-request", self._on_settings_window_closed)

        self.settings_window.present()

    def _on_settings_window_closed(self, window: SettingsWindow) -> bool:
        """Drop the cached settings window reference when it closes."""
        _ = window
        self.settings_window = None
        return False

    def _on_show_time_in_title_changed(self, _settings: object, _key: str) -> None:
        """Update show_time_in_title preference from GSettings."""
        self.show_time_in_title = self.settings.get_boolean("show-time-in-title")
        if not self.show_time_in_title:
            # Restore to original title when disabled
            self.set_title(f"Execute: {self.group_name}")

    def _on_pause_on_blur_changed(self, _settings: object, _key: str) -> None:
        """Update pause_on_blur preference from GSettings."""
        self.pause_on_blur = self.settings.get_boolean("pause-on-blur")

    def _on_window_activity_changed(self, _window: Gtk.ApplicationWindow, _param: object) -> None:
        """Pause the group and emit a notification when the window loses focus."""
        if self.is_active():
            self._has_been_active = True
            return
        if not self._has_been_active or not self.pause_on_blur or self.is_paused:
            return
        if self.group.status != GroupStatus.EXECUTING:
            return

        self.service.pause_group_execution(self.group.id)
        self._stop_timer()
        self.controls.pause_button.set_label("Resume")
        self.is_paused = True
        self.group = self.service.get_group(self.group.id) or self.group
        self._publish_status(force=True)
        self.service.notify_focus_lost(self.group.id)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for group execution window."""
        # Create key event controller
        key_controller = Gtk.EventControllerKey.new()
        self.add_controller(key_controller)

        def on_key_pressed(controller, keyval, keycode, state):  # noqa: ARG001
            """Handle key press events."""
            from gi.repository import Gdk  # type: ignore[import-untyped]

            ctrl = state & Gdk.ModifierType.CONTROL_MASK
            _shift = state & Gdk.ModifierType.SHIFT_MASK

            # Space: Pause/Resume
            if keyval == Gdk.KEY_space:
                self.controls.pause_button.emit("clicked")
                return True

            # Ctrl+P: Pause/Resume (alternative)
            if ctrl and keyval in (Gdk.KEY_p, ord("P")):
                self.controls.pause_button.emit("clicked")
                return True

            # Ctrl+Right: Skip task
            if ctrl and keyval == Gdk.KEY_Right:
                self.controls.skip_button.emit("clicked")
                return True

            # Ctrl+Q: Stop/Quit
            if ctrl and keyval in (Gdk.KEY_q, ord("Q")):
                self.controls.stop_button.emit("clicked")
                return True

            return False

        key_controller.connect("key-pressed", on_key_pressed)

    def _start_timer(self) -> None:
        """Start the group execution timer."""

        def update_timer() -> bool:
            """Update timer display and state."""
            updated_group = self.service.get_group(self.group.id)
            if not updated_group:
                self._stop_timer()
                return False

            self.group = updated_group
            if self.group.status == GroupStatus.EXECUTING:
                self.group = self.service.update_group_elapsed_time(
                    self.group.id,
                    self._elapsed_seconds(),
                )
                self.is_paused = False
                self.controls.pause_button.set_label("Pause")
            elif self.group.status == GroupStatus.PAUSED:
                self.is_paused = True
                self.controls.pause_button.set_label("Resume")

            remaining = self.group.time_remaining_seconds()
            minutes = remaining // 60
            seconds = remaining % 60
            self.timer_display.set_markup(
                f'<span font="JetBrains Mono 48" weight="bold">{minutes:02d}:{seconds:02d}</span>'
            )

            if self.show_time_in_title:
                self.set_title(f"{minutes:02d}:{seconds:02d} - {self.group_name}")

            current_task = self.group.current_task_id()
            self.task_queue.set_current_task(current_task)
            self.task_queue.set_progress(self.group.progress_percent() / 100.0)
            self.stats.update(
                self.group.tasks_completed,
                len(self.group.task_ids),
                self.group.elapsed_time_seconds,
            )
            self._publish_status()

            if self.group.status == GroupStatus.COMPLETED or remaining <= 0:
                self._on_group_completed()
                return False

            return True

        update_timer()
        self.timer_handle = GLib.timeout_add_seconds(1, update_timer)

    def _elapsed_seconds(self) -> int:
        """Calculate elapsed execution time excluding paused time."""
        if self.group.started_at is None:
            return self.group.elapsed_time_seconds

        total_elapsed = int((datetime.now(UTC) - self.group.started_at).total_seconds())
        paused_seconds = self.group.paused_time_seconds
        if self.group.paused_at is not None:
            paused_seconds += int((datetime.now(UTC) - self.group.paused_at).total_seconds())
        return max(self.group.elapsed_time_seconds, total_elapsed - paused_seconds)

    def _publish_status(self, *, force: bool = False) -> None:
        """Broadcast the latest execution state to GNOME integrations."""
        if self.status_interface is None:
            return
        self.status_interface.set_active_group(self.group.id)
        self.status_interface.refresh(force=force)

    def _stop_timer(self) -> None:
        """Stop the timer loop."""
        if self.timer_handle is not None:
            GLib.source_remove(self.timer_handle)
            self.timer_handle = None

    def _on_pause_clicked(self, button: Gtk.Button) -> None:
        """Handle pause button click."""
        if self.is_paused:
            # Resume
            self.service.resume_group_execution(self.group.id)
            self.group = self.service.get_group(self.group.id) or self.group
            button.set_label("Pause")
            self._start_timer()
            self.is_paused = False
            self._publish_status(force=True)
        else:
            # Pause
            self.service.pause_group_execution(self.group.id)
            self.group = self.service.get_group(self.group.id) or self.group
            self._stop_timer()
            button.set_label("Resume")
            self.is_paused = True
            self._publish_status(force=True)

    def _on_skip_clicked(self, button: Gtk.Button) -> None:
        """Handle skip button click."""
        _ = button  # Unused
        if self.group.status == GroupStatus.EXECUTING:
            self.service.skip_task_in_group(self.group.id)
            self.group = self.service.get_group(self.group.id) or self.group
            self._publish_status(force=True)

    def _on_stop_clicked(self, button: Gtk.Button) -> None:
        """Handle stop button click."""
        _ = button  # Unused
        self._stop_timer()
        self.close()

    def _on_group_completed(self) -> None:
        """Handle group completion."""
        self._stop_timer()
        self.controls.pause_button.set_sensitive(False)
        self.controls.skip_button.set_sensitive(False)
        self.controls.stop_button.set_label("Close")
        self.timer_display.set_markup(
            '<span font="JetBrains Mono 48" weight="bold" color="#33d17a">✓</span>'
        )
        if self.status_interface is not None:
            self.status_interface.clear_active_group()
