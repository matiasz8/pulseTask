"""TaskList - Task list view for PulseTask V2.

Displays all tasks with inline actions and quick-add functionality.
"""

from __future__ import annotations

from collections.abc import Callable

from gi.repository import Gtk, Pango

from pulse_task.core.task import Task, TaskStatus


class TaskListView(Gtk.Box):
    """Task list view displaying all tasks with actions.

    Features:
    - Grouped display (active/archived)
    - Task selection → focus view
    - Quick-add task dialog
    - Inline action buttons (start, edit, archive)
    - Keyboard navigation
    """

    def __init__(
        self,
        tasks: list[Task],
        on_select_task: Callable[[Task], None] | None = None,
        on_create_task: Callable[[str, int], None] | None = None,
        on_action: Callable[[str, str], None] | None = None,
        show_archived: bool = False,
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.tasks = tasks
        self.on_select_task = on_select_task
        self.on_create_task = on_create_task
        self.on_action = on_action
        self.show_archived = show_archived

        # Set up main container
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_vexpand(True)

        # Build the UI
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the task list UI."""
        # Header with title and create button
        header = self._build_header()
        self.append(header)

        # Scrollable task list
        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_hexpand(True)

        # Main content box
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16,
        )
        content.set_margin_top(8)

        # Separate active and archived tasks
        active_tasks = [t for t in self.tasks if t.status != TaskStatus.ARCHIVED]
        archived_tasks = [t for t in self.tasks if t.status == TaskStatus.ARCHIVED]

        # Active tasks section
        if active_tasks:
            active_section = self._build_task_section(
                "Active Tasks", active_tasks, show_header=True
            )
            content.append(active_section)

        # Archived tasks section (if enabled)
        if self.show_archived and archived_tasks:
            archived_section = self._build_task_section(
                "Archived Tasks", archived_tasks, show_header=True
            )
            content.append(archived_section)

        # Empty state
        if not active_tasks and not (self.show_archived and archived_tasks):
            empty_state = self._build_empty_state()
            content.append(empty_state)

        scroller.set_child(content)
        self.append(scroller)

    def _build_header(self) -> Gtk.Box:
        """Build the header with title and create button."""
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
        )
        header.set_margin_bottom(8)

        # Title
        title = Gtk.Label(xalign=0)
        title.set_markup("<b>Tasks</b>")
        title.set_hexpand(True)
        header.append(title)

        # Create button
        create_btn = Gtk.Button(label="+ New Task")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self._on_create_clicked)
        header.append(create_btn)

        return header

    def _build_task_section(
        self,
        title: str,
        tasks: list[Task],
        show_header: bool = True,
    ) -> Gtk.Box:
        """Build a section of tasks."""
        section = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )

        # Section header
        if show_header:
            header_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=8,
            )

            header_label = Gtk.Label(xalign=0, label=title)
            header_label.add_css_class("dim-label")
            header_box.append(header_label)

            count_label = Gtk.Label(xalign=1, label=f"({len(tasks)})")
            count_label.add_css_class("dim-label")
            header_box.append(count_label)

            section.append(header_box)

        # Task list box
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box.add_css_class("boxed-list")

        for task in tasks:
            # Check if task has parent (subtask)
            if task.parent_task_id is not None:
                continue  # Skip subtasks, they're shown in parent's section

            row = self._create_task_row(task)
            list_box.append(row)

            # Add subtasks if any
            subtasks = [t for t in self.tasks if t.parent_task_id == task.id]
            for subtask in subtasks:
                subtask_row = self._create_task_row(subtask, is_subtask=True)
                list_box.append(subtask_row)

        section.append(list_box)

        return section

    def _create_task_row(self, task: Task, is_subtask: bool = False) -> Gtk.ListBoxRow:
        """Create a task row for the list."""
        row = Gtk.ListBoxRow()
        row.set_focusable(True)

        # Main container
        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
        )
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12 if is_subtask else 16)
        box.set_margin_end(16)

        # Add left border for running/paused tasks
        if task.status == TaskStatus.RUNNING:
            box.add_css_class("task-card-running")
        elif task.status == TaskStatus.PAUSED:
            box.add_css_class("task-card-paused")
        elif task.status == TaskStatus.EXPIRED:
            box.add_css_class("task-card-expired")
        elif task.status == TaskStatus.COMPLETED:
            box.add_css_class("task-card-completed")
        elif task.status == TaskStatus.ARCHIVED:
            box.add_css_class("task-card-archived")

        # Task info
        info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )
        info_box.set_hexpand(True)

        # Title row
        title_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        # Prefix for subtasks
        prefix = "↳ " if is_subtask else ""

        # Title label
        title_label = Gtk.Label(xalign=0)
        title_label.set_markup(f"{prefix}<b>{self._escape_markup(task.title)}</b>")
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_hexpand(True)
        title_row.append(title_label)

        # Status badge
        status_label = Gtk.Label(label=task.status.value.upper())
        status_label.add_css_class("status-badge")
        status_label.add_css_class(f"status-{task.status.value}")
        title_row.append(status_label)

        info_box.append(title_row)

        # Time info
        remaining = task.remaining_seconds
        duration = task.duration_seconds
        time_text = f"{self._format_seconds(remaining)} / {self._format_seconds(duration)}"

        time_label = Gtk.Label(xalign=0, label=time_text)
        time_label.add_css_class("dim-label")
        time_label.add_css_class("countdown")
        time_label.add_css_class("countdown-xs")
        info_box.append(time_label)

        box.append(info_box)

        # Action buttons
        actions_box = self._build_task_actions(task)
        box.append(actions_box)

        # Make row clickable
        event_controller = Gtk.GestureClick()
        event_controller.connect("released", self._on_row_clicked, task)
        box.add_controller(event_controller)

        row.set_child(box)

        return row

    def _build_task_actions(self, task: Task) -> Gtk.Box:
        """Build action buttons for a task."""
        actions = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4,
        )

        # Start/Resume/Pause button
        if task.status == TaskStatus.PENDING:
            btn = self._create_icon_button(
                "media-playback-start-symbolic",
                "Start",
                lambda: self._on_action(task.id, "start"),
            )
            actions.append(btn)
        elif task.status == TaskStatus.PAUSED:
            btn = self._create_icon_button(
                "media-playback-start-symbolic",
                "Resume",
                lambda: self._on_action(task.id, "resume"),
            )
            actions.append(btn)
        elif task.status == TaskStatus.RUNNING:
            btn = self._create_icon_button(
                "media-playback-pause-symbolic",
                "Pause",
                lambda: self._on_action(task.id, "pause"),
            )
            actions.append(btn)

        # Complete button (for active tasks)
        if task.status in {TaskStatus.PENDING, TaskStatus.PAUSED, TaskStatus.RUNNING}:
            btn = self._create_icon_button(
                "object-select-symbolic",
                "Complete",
                lambda: self._on_action(task.id, "complete"),
            )
            actions.append(btn)

        # Archive/Restore button
        if task.status != TaskStatus.ARCHIVED:
            btn = self._create_icon_button(
                "mail-archive-symbolic",
                "Archive",
                lambda: self._on_action(task.id, "archive"),
            )
            actions.append(btn)
        else:
            btn = self._create_icon_button(
                "document-revert-symbolic",
                "Restore",
                lambda: self._on_action(task.id, "restore"),
            )
            actions.append(btn)

        return actions

    def _create_icon_button(
        self,
        icon_name: str,
        tooltip: str,
        callback: Callable,
    ) -> Gtk.Button:
        """Create a small icon button."""
        button = Gtk.Button()
        button.add_css_class("flat")
        button.add_css_class("icon-button")
        button.set_tooltip_text(tooltip)
        button.set_child(Gtk.Image.new_from_icon_name(icon_name))
        button.connect("clicked", lambda btn: callback())
        return button

    def _build_empty_state(self) -> Gtk.Box:
        """Build empty state when no tasks exist."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        box.set_vexpand(True)

        # Icon
        icon = Gtk.Image.new_from_icon_name("task-complete-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("dim-label")
        box.append(icon)

        # Title
        title = Gtk.Label(label="No tasks yet")
        title.add_css_class("title-3")
        box.append(title)

        # Description
        desc = Gtk.Label(label="Create your first task to get started")
        desc.add_css_class("dim-label")
        box.append(desc)

        # Create button
        create_btn = Gtk.Button(label="+ Create Task")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self._on_create_clicked)
        box.append(create_btn)

        return box

    def _on_row_clicked(self, gesture: Gtk.GestureClick, n_press: int, task: Task) -> None:
        """Handle row click."""
        if self.on_select_task:
            self.on_select_task(task)

    def _on_action(self, task_id: str, action: str) -> None:
        """Handle action button click."""
        if self.on_action:
            self.on_action(task_id, action)

    def _on_create_clicked(self, button: Gtk.Button) -> None:
        """Handle create button click."""
        if self.on_create_task:
            # Show create dialog
            self._show_create_dialog()

    def _show_create_dialog(self) -> None:
        """Show a dialog to create a new task."""
        # Get the root window
        root = self.get_root()

        dialog = Gtk.Dialog(
            title="Create Task",
            transient_for=root,
            modal=True,
        )
        dialog.set_default_size(400, 300)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Create", Gtk.ResponseType.OK)

        content = dialog.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        # Title entry
        title_label = Gtk.Label(xalign=0, label="Title")
        content.append(title_label)

        title_entry = Gtk.Entry()
        title_entry.set_placeholder_text("Task title")
        title_entry.set_hexpand(True)
        content.append(title_entry)

        # Duration spinner
        duration_label = Gtk.Label(xalign=0, label="Duration (minutes)")
        content.append(duration_label)

        duration_spin = Gtk.SpinButton.new_with_range(1, 480, 1)
        duration_spin.set_value(25)  # Default 25 minutes
        content.append(duration_spin)

        dialog.connect(
            "response",
            self._on_create_response,
            title_entry,
            duration_spin,
        )

        # Focus title entry
        title_entry.grab_focus()

        dialog.present()

    def _on_create_response(
        self,
        dialog: Gtk.Dialog,
        response_id: int,
        title_entry: Gtk.Entry,
        duration_spin: Gtk.SpinButton,
    ) -> None:
        """Handle create dialog response."""
        if response_id == Gtk.ResponseType.OK:
            title = title_entry.get_text().strip()
            if title and self.on_create_task:
                duration_minutes = duration_spin.get_value_as_int()
                self.on_create_task(title, duration_minutes * 60)

        dialog.close()

    def update_tasks(self, tasks: list[Task]) -> None:
        """Update the task list."""
        self.tasks = tasks

        # Remove all children
        while True:
            child = self.get_first_child()
            if child is None:
                break
            self.remove(child)

        # Rebuild UI
        self._build_ui()

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        """Format seconds to MM:SS or HH:MM:SS."""
        if seconds < 0:
            seconds = 0

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

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
