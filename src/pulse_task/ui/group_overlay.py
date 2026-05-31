"""Group Execution Overlay.

Provides a compact, non-intrusive floating window for group task execution
with minimal controls. Can be toggled with a keyboard shortcut.
"""
# mypy: ignore-errors

from __future__ import annotations

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Gdk", "4.0")  # noqa: E402

from gi.repository import GLib, Gtk  # noqa: E402 # type: ignore[import-untyped]

from pulse_task.core.group import TaskGroup  # noqa: E402
from pulse_task.core.group_service import GroupService  # noqa: E402


class GroupOverlay(Gtk.Window):
    """Compact floating overlay for group execution."""

    def __init__(
        self,
        group: TaskGroup,
        service: GroupService,
    ) -> None:
        """Initialize group overlay.

        Args:
            group: TaskGroup to execute
            service: GroupService for managing execution
        """
        super().__init__(type=Gtk.WindowType.POPUP)
        self.group = group
        self.service = service
        self.timer_handle: int | None = None
        self.is_paused = False

        # Window setup
        self.set_title(f"PulseTask: {group.name}")
        self.set_modal(False)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(320, 120)
        self.add_css_class("group-overlay")

        # Set initial opacity
        self.set_opacity(0.95)

        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)

        # Timer display
        self.timer_label = Gtk.Label()
        self.timer_label.add_css_class("overlay-timer")
        self.timer_label.set_markup(
            '<span font="JetBrains Mono 24" weight="bold">00:00</span>'
        )
        vbox.append(self.timer_label)

        # Task name
        self.task_label = Gtk.Label(label=group.task_ids[0] if group.task_ids else "")
        self.task_label.add_css_class("overlay-task")
        self.task_label.set_ellipsize(3)  # End ellipsize
        vbox.append(self.task_label)

        # Controls box
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hbox.set_halign(Gtk.Align.CENTER)

        # Pause button
        self.pause_btn = Gtk.Button(label="Pause")
        self.pause_btn.set_size_request(60, 24)
        self.pause_btn.connect("clicked", self._on_pause_clicked)
        hbox.append(self.pause_btn)

        # Skip button
        self.skip_btn = Gtk.Button(label="Skip")
        self.skip_btn.set_size_request(60, 24)
        self.skip_btn.connect("clicked", self._on_skip_clicked)
        hbox.append(self.skip_btn)

        vbox.append(hbox)

        self.set_child(vbox)

        # Connect focus events for opacity changes
        self.connect("focus-in-event", self._on_focus_in)
        self.connect("focus-out-event", self._on_focus_out)

        # Start timer
        self._start_timer()

    def _start_timer(self) -> None:
        """Start the overlay timer."""

        def update_timer() -> bool:
            """Update timer display."""
            updated_group = self.service.get_group(self.group.id)
            if not updated_group:
                self._stop_timer()
                return False

            self.group = updated_group

            # Update timer
            remaining = self.group.time_remaining_seconds()
            minutes = remaining // 60
            seconds = remaining % 60
            self.timer_label.set_markup(
                f'<span font="JetBrains Mono 24" weight="bold">'
                f"{minutes:02d}:{seconds:02d}</span>"
            )

            # Update task name
            current_task = self.group.current_task_id()
            if current_task:
                self.task_label.set_text(current_task)
            else:
                self.task_label.set_text("Complete")

            # Check for completion
            if remaining <= 0:
                self._stop_timer()
                return False

            return True  # Keep running

        self.timer_handle = GLib.timeout_add(100, update_timer)

    def _stop_timer(self) -> None:
        """Stop the timer loop."""
        if self.timer_handle is not None:
            GLib.source_remove(self.timer_handle)
            self.timer_handle = None

    def _on_pause_clicked(self, button: Gtk.Button) -> None:
        """Handle pause button click."""
        if self.is_paused:
            self.service.resume_group_execution(self.group.id)
            button.set_label("Pause")
            self._start_timer()
            self.is_paused = False
        else:
            self.service.pause_group_execution(self.group.id)
            self._stop_timer()
            button.set_label("Resume")
            self.is_paused = True

    def _on_skip_clicked(self, button: Gtk.Button) -> None:
        """Handle skip button click."""
        _ = button  # Unused
        self.service.skip_task_in_group(self.group.id)

    def _on_focus_in(self, widget: object, event: object) -> None:  # type: ignore[arg-type]
        """Increase opacity on focus."""
        self.set_opacity(1.0)

    def _on_focus_out(self, widget: object, event: object) -> None:  # type: ignore[arg-type]
        """Reduce opacity on focus out."""
        self.set_opacity(0.7)

    def toggle_visibility(self) -> None:
        """Toggle overlay visibility."""
        if self.get_visible():
            self.hide()
        else:
            self.present()

    def cleanup(self) -> None:
        """Clean up resources."""
        self._stop_timer()
