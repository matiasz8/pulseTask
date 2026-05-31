"""Group Task Execution Window.

Provides a dedicated interface for executing task groups with visual feedback
on timer, task progress, and control buttons.
"""
# mypy: ignore-errors

from __future__ import annotations

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Adw", "1")  # noqa: E402

from gi.repository import Adw, GLib, Gtk  # noqa: E402 # type: ignore[import-untyped]

from pulse_task.core.group import GroupStatus, TaskGroup  # noqa: E402
from pulse_task.core.group_service import GroupService  # noqa: E402


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
    """Control buttons for group execution."""

    def __init__(self) -> None:
        """Initialize control panel."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_halign(Gtk.Align.CENTER)

        # Play/Pause button
        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.add_css_class("suggested-action")
        self.append(self.pause_button)

        # Skip button
        self.skip_button = Gtk.Button(label="Skip Task")
        self.append(self.skip_button)

        # Stop button
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.add_css_class("destructive-action")
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
    ) -> None:
        """Initialize group execution window.

        Args:
            app: Adwaita application instance
            group: TaskGroup to execute
            service: GroupService for managing execution
        """
        super().__init__(application=app)
        self.group = group
        self.service = service
        self.timer_handle: int | None = None
        self.is_paused = False

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

        # Title
        title_label = Gtk.Label(label=group.name)
        title_label.add_css_class("title-2")
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

        self.set_child(vbox)

        # Ensure group is started
        if group.status == GroupStatus.IDLE:
            self.service.start_group_execution(group.id)
            updated = self.service.get_group(group.id)
            assert updated is not None
            self.group = updated

        # Start timer
        self._start_timer()

    def _start_timer(self) -> None:
        """Start the group execution timer."""

        def update_timer() -> bool:
            """Update timer display and state."""
            # Fetch latest group state
            updated_group = self.service.get_group(self.group.id)
            if not updated_group:
                self._stop_timer()
                return False

            self.group = updated_group

            # Update timer display
            remaining = self.group.time_remaining_seconds()
            minutes = remaining // 60
            seconds = remaining % 60
            self.timer_display.set_markup(
                f'<span font="JetBrains Mono 48" weight="bold">'
                f"{minutes:02d}:{seconds:02d}</span>"
            )

            # Update task queue
            current_task = self.group.current_task_id()
            self.task_queue.set_current_task(current_task)

            # Update progress
            progress = self.group.progress_percent() / 100.0
            self.task_queue.set_progress(progress)

            # Update stats
            self.stats.update(
                self.group.tasks_completed,
                len(self.group.task_ids),
                self.group.elapsed_time_seconds,
            )

            # Check for completion
            if self.group.status == GroupStatus.COMPLETED:
                self._on_group_completed()
                return False

            # Check for expiration
            if remaining <= 0:
                self._on_group_completed()
                return False

            return True  # Keep timer running

        self.timer_handle = GLib.timeout_add(100, update_timer)

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
            button.set_label("Pause")
            self._start_timer()
            self.is_paused = False
        else:
            # Pause
            self.service.pause_group_execution(self.group.id)
            self._stop_timer()
            button.set_label("Resume")
            self.is_paused = True

    def _on_skip_clicked(self, button: Gtk.Button) -> None:
        """Handle skip button click."""
        _ = button  # Unused
        if self.group.status == GroupStatus.EXECUTING:
            self.service.skip_task_in_group(self.group.id)

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
            '<span font="JetBrains Mono 48" weight="bold" '
            'color="#33d17a">✓</span>'
        )
