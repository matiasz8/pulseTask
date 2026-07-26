"""FocusView - Focus-first main view for PulseTask V2.

Displays the current task with a large countdown, subtask progress,
and state-based controls. This is the primary interaction surface
when a task is active.
"""

from __future__ import annotations

from collections.abc import Callable

from gi.repository import Gtk, Pango

from pulse_task.core.task import Task, TaskStatus
from pulse_task.ui.countdown_widget import CountdownSize, CountdownStatus, CountdownWidget

SNOOZE_OPTIONS = [5, 10, 15]


class FocusView(Gtk.Box):
    """Focus-first main view for an active task.

    Features:
    - Task title and description display
    - Large countdown display with progress ring
    - Subtask progress list with completion markers
    - State-based controls (Start, Pause, Resume, Complete, Reset, Snooze)
    - Keyboard shortcut hints

    Visual layout:
    ┌─────────────────────────────────────────────┐
    │                  FOCUS VIEW                 │
    ├─────────────────────────────────────────────┤
    │              Task Title Here                │
    │        Optional description text            │
    │         ┌─────────────────────┐             │
    │         │     12:34 / 25:00   │             │
    │         │   ████████░░░░░░░   │             │
    │         └─────────────────────┘             │
    │    Steps Progress                2/4        │
    │    ✓ Step 1 (completed)                    │
    │    → Step 2 (current)                      │
    │      Step 3 (future)                       │
    │      Step 4 (future)                       │
    │    [ ▶ Start ]  [ Space ]                  │
    └─────────────────────────────────────────────┘
    """

    def __init__(
        self,
        on_start: Callable[[], None] | None = None,
        on_pause: Callable[[], None] | None = None,
        on_resume: Callable[[], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        on_reset: Callable[[], None] | None = None,
        on_snooze: Callable[[int], None] | None = None,
        on_complete_subtask: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.on_start = on_start
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_complete = on_complete
        self.on_reset = on_reset
        self.on_snooze = on_snooze
        self.on_complete_subtask = on_complete_subtask

        self._task: Task | None = None

        # Main content container (centered)
        self._content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self._content.set_vexpand(True)
        self._content.set_hexpand(True)
        self._content.set_margin_top(48)
        self._content.set_margin_bottom(48)
        self._content.set_margin_start(48)
        self._content.set_margin_end(48)
        self._content.add_css_class("focus-view")

        self.append(self._content)

        # Build empty state initially
        self._build_empty_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_task(self, task: Task | None) -> None:
        """Update the view with a new or updated task."""
        self._task = task
        self._rebuild()

    # ------------------------------------------------------------------
    # Internal builders
    # ------------------------------------------------------------------

    def _rebuild(self) -> None:
        """Rebuild the entire content area."""
        # Clear existing children
        child = self._content.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._content.remove(child)
            child = next_child

        if self._task is None:
            self._build_empty_state()
            return

        match self._task.status:
            case TaskStatus.PENDING:
                self._build_pending_view()
            case TaskStatus.RUNNING:
                self._build_running_view()
            case TaskStatus.PAUSED:
                self._build_paused_view()
            case TaskStatus.EXPIRED:
                self._build_expired_view()
            case TaskStatus.COMPLETED:
                self._build_completed_view()
            case _:
                self._build_empty_state()

    def _build_empty_state(self) -> None:
        """Empty state when no task is selected."""
        icon = Gtk.Image.new_from_icon_name("appointment-soon-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("dim-label")
        self._content.append(icon)

        title = Gtk.Label(label="No task selected")
        title.add_css_class("title-2")
        self._content.append(title)

        desc = Gtk.Label(label="Select or create a task to begin focusing")
        desc.add_css_class("dim-label")
        self._content.append(desc)

    def _build_pending_view(self) -> None:
        """View for a task that hasn't started yet."""
        assert self._task is not None
        self._append_title(self._task.title)
        self._append_description(self._task.description)
        self._append_countdown()
        self._append_subtasks()
        self._append_spacer()
        self._append_button_row(
            ("Start", "media-playback-start-symbolic", "suggested-action", self._on_start_clicked),
        )
        self._append_keyboard_hint("Space", "to start")

    def _build_running_view(self) -> None:
        """View for a currently running task."""
        assert self._task is not None
        self._append_title(self._task.title)
        self._append_description(self._task.description)
        self._append_countdown()
        self._append_subtasks()
        self._append_spacer()
        self._append_button_row(
            ("Pause", "media-playback-pause-symbolic", "btn-secondary", self._on_pause_clicked),
            ("Complete", "object-select-symbolic", "btn-success", self._on_complete_clicked),
        )
        self._append_keyboard_hint_pair("Space", "pause", "Enter", "complete")

    def _build_paused_view(self) -> None:
        """View for a paused task."""
        assert self._task is not None
        self._append_title(self._task.title)
        self._append_description(self._task.description)
        self._append_countdown()
        self._append_subtasks()
        self._append_spacer()
        self._append_button_row(
            (
                "Resume",
                "media-playback-start-symbolic",
                "suggested-action",
                self._on_resume_clicked,
            ),
            ("Reset", "view-refresh-symbolic", "flat", self._on_reset_clicked),
        )
        self._append_keyboard_hint_pair("Space", "resume", "Ctrl+R", "reset")

    def _build_expired_view(self) -> None:
        """View for an expired task."""
        assert self._task is not None
        self._append_title(self._task.title, css_class="text-expired")
        self._append_description(self._task.description)
        self._append_countdown()
        self._append_subtasks()
        self._append_spacer()

        # Main actions
        self._append_button_row(
            ("Mark Complete", "object-select-symbolic", "btn-success", self._on_complete_clicked),
            ("Reset", "view-refresh-symbolic", "flat", self._on_reset_clicked),
        )

        # Snooze row
        self._append_snooze_row()

        self._append_status_text("Time expired — wrap up or extend")

    def _build_completed_view(self) -> None:
        """View for a completed task."""
        assert self._task is not None

        icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        icon.set_pixel_size(64)
        icon.add_css_class("text-completed")
        self._content.append(icon)

        self._append_title(self._task.title, css_class="text-completed")
        self._append_countdown()
        self._append_spacer()
        self._append_button_row(
            ("Start Again", "view-refresh-symbolic", "flat", self._on_reset_clicked),
        )

    # ------------------------------------------------------------------
    # Builder helpers
    # ------------------------------------------------------------------

    def _append_title(self, title: str, css_class: str = "") -> None:
        label = Gtk.Label(xalign=0)
        label.set_markup(f"<span size='x-large' weight='bold'>{self._escape(title)}</span>")
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(60)
        label.set_wrap(True)
        label.set_halign(Gtk.Align.CENTER)
        if css_class:
            label.add_css_class(css_class)
        self._content.append(label)

    def _append_description(self, description: str) -> None:
        if not description:
            return
        label = Gtk.Label(xalign=0, label=description)
        label.add_css_class("dim-label")
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(50)
        label.set_halign(Gtk.Align.CENTER)
        self._content.append(label)

    def _append_countdown(self) -> None:
        assert self._task is not None
        self._countdown = CountdownWidget(
            size=CountdownSize.XL,
            show_progress=True,
        )
        self._sync_countdown()
        box = Gtk.Box(halign=Gtk.Align.CENTER)
        box.set_margin_top(32)
        box.set_margin_bottom(32)
        box.append(self._countdown)
        self._content.append(box)

    def _sync_countdown(self) -> None:
        """Sync countdown widget with current task state."""
        if not hasattr(self, "_countdown") or self._task is None:
            return
        elapsed = self._task.duration_seconds - self._task.remaining_seconds
        self._countdown.elapsed = elapsed
        self._countdown.duration = self._task.duration_seconds

        status_map = {
            TaskStatus.PENDING: CountdownStatus.PENDING,
            TaskStatus.RUNNING: CountdownStatus.RUNNING,
            TaskStatus.PAUSED: CountdownStatus.PAUSED,
            TaskStatus.EXPIRED: CountdownStatus.EXPIRED,
            TaskStatus.COMPLETED: CountdownStatus.COMPLETED,
        }
        self._countdown.status = status_map.get(self._task.status, CountdownStatus.PENDING)

    def _append_subtasks(self) -> None:
        """Append subtask progress list if task has subtasks."""
        assert self._task is not None
        if not self._task.subtasks:
            return

        # Header
        header_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
        )
        header_box.set_margin_bottom(12)

        header_label = Gtk.Label(label="Steps Progress")
        header_label.add_css_class("dim-label")
        header_box.append(header_label)

        completed = sum(1 for st in self._task.subtasks if st.status == TaskStatus.COMPLETED)
        total = len(self._task.subtasks)
        count_label = Gtk.Label(label=f"{completed}/{total}")
        count_label.add_css_class("dim-label")
        count_label.add_css_class("countdown")
        count_label.add_css_class("countdown-xs")
        header_box.append(count_label)

        self._content.append(header_box)

        # Subtask list
        list_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
            halign=Gtk.Align.CENTER,
        )
        list_box.set_size_request(300, -1)

        for index, subtask in enumerate(self._task.subtasks):
            is_past = subtask.status == TaskStatus.COMPLETED
            is_current = index == self._task.current_subtask_index and not is_past

            row = self._build_subtask_row(subtask, index, is_past, is_current)
            list_box.append(row)

        self._content.append(list_box)

    def _build_subtask_row(
        self,
        subtask: Task,
        index: int,
        is_past: bool,
        is_current: bool,
    ) -> Gtk.Box:
        """Build a single subtask row."""
        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        row.set_margin_top(4)
        row.set_margin_bottom(4)
        row.set_margin_start(12)
        row.set_margin_end(12)

        if is_past:
            row.add_css_class("subtask-completed")
        elif is_current:
            row.add_css_class("subtask-current")
        else:
            row.add_css_class("subtask-future")

        # Step indicator
        if is_past:
            indicator = Gtk.Image.new_from_icon_name("object-select-symbolic")
        else:
            indicator = Gtk.Label(label=str(index + 1))
        row.append(indicator)

        # Title
        title_label = Gtk.Label(xalign=0, label=subtask.title)
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_hexpand(True)
        if is_past:
            title_label.add_css_class("dim-label")
        row.append(title_label)

        # Click to complete (if running/expired and not past)
        active_states = {TaskStatus.RUNNING, TaskStatus.EXPIRED}
        if not is_past and self._task and self._task.status in active_states:
            event_controller = Gtk.GestureClick()
            event_controller.connect("released", self._on_subtask_clicked, subtask.id)
            row.add_controller(event_controller)

        return row

    def _append_spacer(self) -> None:
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self._content.append(spacer)

    def _append_button_row(self, *buttons: tuple[str, str, str, Callable]) -> None:
        """Append a row of action buttons.

        Each tuple: (label, icon, css_class, callback)
        """
        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
        )
        row.set_margin_top(16)

        for label, _icon, css_class, callback in buttons:
            btn = Gtk.Button()
            btn.set_label(label)
            btn.add_css_class(css_class)
            btn.connect("clicked", lambda _b, cb=callback: cb())
            row.append(btn)

        self._content.append(row)

    def _append_snooze_row(self) -> None:
        """Append snooze buttons for expired tasks."""
        if self.on_snooze is None:
            return

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
        )
        row.set_margin_top(8)

        label = Gtk.Label(label="Snooze:")
        label.add_css_class("dim-label")
        row.append(label)

        for minutes in SNOOZE_OPTIONS:
            btn = Gtk.Button(label=f"+{minutes}m")
            btn.add_css_class("flat")
            mins = minutes  # capture
            btn.connect("clicked", lambda _b, m=mins: self.on_snooze(m * 60))
            row.append(btn)

        self._content.append(row)

    def _append_keyboard_hint(self, key: str, action: str) -> None:
        """Append a keyboard shortcut hint."""
        hint = Gtk.Label()
        hint.set_markup(
            f'<span size="small" foreground="#888888">Press <b>{key}</b> {action}</span>'
        )
        hint.set_halign(Gtk.Align.CENTER)
        hint.set_margin_top(12)
        self._content.append(hint)

    def _append_keyboard_hint_pair(self, key1: str, action1: str, key2: str, action2: str) -> None:
        """Append two keyboard shortcut hints."""
        hint = Gtk.Label()
        hint.set_markup(
            f'<span size="small" foreground="#888888">'
            f"Press <b>{key1}</b> {action1} · <b>{key2}</b> {action2}"
            f"</span>"
        )
        hint.set_halign(Gtk.Align.CENTER)
        hint.set_margin_top(12)
        self._content.append(hint)

    def _append_status_text(self, text: str) -> None:
        """Append a status message."""
        label = Gtk.Label(label=text)
        label.add_css_class("dim-label")
        label.set_halign(Gtk.Align.CENTER)
        label.set_margin_top(8)
        self._content.append(label)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_start_clicked(self) -> None:
        if self.on_start:
            self.on_start()

    def _on_pause_clicked(self) -> None:
        if self.on_pause:
            self.on_pause()

    def _on_resume_clicked(self) -> None:
        if self.on_resume:
            self.on_resume()

    def _on_complete_clicked(self) -> None:
        if self.on_complete:
            self.on_complete()

    def _on_reset_clicked(self) -> None:
        if self.on_reset:
            self.on_reset()

    def _on_subtask_clicked(self, _gesture: Gtk.GestureClick, _n: int, subtask_id: str) -> None:
        if self.on_complete_subtask:
            self.on_complete_subtask(subtask_id)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(text: str) -> str:
        """Escape text for Pango markup."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;")
        )
