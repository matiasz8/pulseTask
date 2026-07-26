"""TaskCard - Individual task display component for PulseTask V2.

Provides a reusable task card with state-based styling and actions.
"""

from __future__ import annotations

from gi.repository import Gtk, Pango

from pulse_task.core.task import Task, TaskStatus


class TaskCard(Gtk.ListBoxRow):
    """A task card displaying task information and quick actions.

    Features:
    - State-based visual styling (running, paused, expired, etc.)
    - Title, description, and metadata display
    - Contextual action buttons based on task state
    - Keyboard accessibility
    """

    def __init__(self, task: Task, is_active: bool = False) -> None:
        super().__init__()

        self.task = task
        self.is_active = is_active

        # Build the card UI
        self._build_ui()

        # Apply styling based on task state
        self._apply_style()

        # Set up keyboard navigation
        self.set_focusable(True)

    def _build_ui(self) -> None:
        """Build the card's internal structure."""
        # Main container
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(16)

        # Top row: Title + Status badge
        top_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
        )

        # Title
        self.title_label = Gtk.Label(xalign=0)
        self.title_label.set_markup(f"<b>{self._escape_markup(self.task.title)}</b>")
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.title_label.set_hexpand(True)
        top_row.append(self.title_label)

        # Status badge
        self.status_badge = Gtk.Label(label=self.task.status.value.upper())
        self.status_badge.add_css_class("status-badge")
        self.status_badge.add_css_class(f"status-{self.task.status.value}")
        top_row.append(self.status_badge)

        self.main_box.append(top_row)

        # Description (if exists)
        if self.task.description:
            desc_label = Gtk.Label(xalign=0, label=self.task.description)
            desc_label.set_ellipsize(Pango.EllipsizeMode.END)
            desc_label.set_max_width_chars(60)
            desc_label.add_css_class("dim-label")
            self.main_box.append(desc_label)

        # Time info row
        time_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=16,
        )

        # Remaining time
        remaining = self.task.remaining_seconds
        self.time_label = Gtk.Label(
            xalign=0,
            label=(
                f"Remaining: {self._format_seconds(remaining)}"
                f" of {self._format_seconds(self.task.duration_seconds)}"
            ),
        )
        time_row.append(self.time_label)

        # Duration in human-readable format
        duration_minutes = max(1, self.task.duration_seconds // 60)
        duration_label = Gtk.Label(
            xalign=0,
            label=f"({self._format_minutes_human(duration_minutes)})",
        )
        duration_label.add_css_class("dim-label")
        time_row.append(duration_label)

        self.main_box.append(time_row)

        # Actions row
        self.actions_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        self._build_actions()
        self.main_box.append(self.actions_box)

        # Add to row
        self.set_child(self.main_box)

    def _build_actions(self) -> None:
        """Build action buttons based on task state."""
        # Clear existing actions
        while True:
            child = self.actions_box.get_first_child()
            if child is None:
                break
            self.actions_box.remove(child)

        # Add actions based on task status
        if self.task.status in {TaskStatus.PENDING, TaskStatus.PAUSED}:
            start_label = "Start" if self.task.status == TaskStatus.PENDING else "Resume"
            start_icon = (
                "media-playback-start-symbolic"
                if self.task.status == TaskStatus.PENDING
                else "view-refresh-symbolic"
            )
            self._add_action_button(start_icon, start_label, "start")

        elif self.task.status == TaskStatus.RUNNING:
            self._add_action_button("media-playback-pause-symbolic", "Pause", "pause")

        # Complete button for active states
        if self.task.status in {TaskStatus.PENDING, TaskStatus.PAUSED, TaskStatus.RUNNING}:
            self._add_action_button("object-select-symbolic", "Complete", "complete")

        # Reset button for non-archived
        if self.task.status != TaskStatus.ARCHIVED:
            self._add_action_button("view-refresh-symbolic", "Reset", "reset")

        # Edit button
        self._add_action_button("document-edit-symbolic", "Edit", "edit")

        # Archive/Restore
        if self.task.status != TaskStatus.ARCHIVED:
            self._add_action_button("mail-archive-symbolic", "Archive", "archive")
        else:
            self._add_action_button("document-revert-symbolic", "Unarchive", "unarchive")

        # Delete (always available)
        self._add_action_button("user-trash-symbolic", "Delete", "delete")

        # Add subtask button (for parent tasks only)
        if self.task.parent_task_id is None and self.task.status != TaskStatus.ARCHIVED:
            self._add_action_button("list-add-symbolic", "Add Subtask", "add_subtask")

        # Start block button (for parent tasks with subtasks)
        if self.task.parent_task_id is None and self.task.status != TaskStatus.ARCHIVED:
            # Check if has subtasks (would need service, but for now just show if not archived)
            self._add_action_button("media-playback-start-symbolic", "Start Block", "start_block")

    def _add_action_button(self, icon_name: str, tooltip: str, action_type: str) -> None:
        """Add an action button to the actions box."""
        button = Gtk.Button()
        button.add_css_class("flat")
        button.set_tooltip_text(tooltip)
        button.set_child(Gtk.Image.new_from_icon_name(icon_name))
        button.connect("clicked", self._on_action_clicked, action_type)
        self.actions_box.append(button)

    def _on_action_clicked(self, button: Gtk.Button, action_type: str) -> None:
        """Handle action button clicks."""
        # Emit a custom signal with the action type
        self.emit("action-clicked", self.task.id, action_type)

    def _apply_style(self) -> None:
        """Apply CSS classes based on task state."""
        # Add base task card class
        self.main_box.add_css_class("task-card")

        # Add state-specific class
        state_class = f"task-card-{self.task.status.value}"
        self.main_box.add_css_class(state_class)

        # If active, add active class
        if self.is_active:
            self.main_box.add_css_class("task-card-active")

    def _format_seconds(self, seconds: int) -> str:
        """Format seconds to MM:SS or HH:MM:SS."""
        if seconds < 0:
            seconds = 0

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _format_minutes_human(self, minutes: int) -> str:
        """Format minutes to human-readable string."""
        if minutes >= 60:
            hours = minutes // 60
            rem = minutes % 60
            if rem == 0:
                return f"{hours}h"
            return f"{hours}h and {rem} min"
        return f"{minutes} min"

    @staticmethod
    def _escape_markup(text: str) -> str:
        """Escape text for Pango markup."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;")
        )


# Define custom signals
go = Gtk.Signal(
    "action-clicked",
    (str, str),  # task_id, action_type
)
