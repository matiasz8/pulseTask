"""CompactOverlay - Always-on-top overlay window for PulseTask V2.

Provides a compact, draggable timer window for multitasking.
Supports three density modes: normal, compact, and ultra-compact.
"""

from __future__ import annotations

from collections.abc import Callable

from gi.repository import Gdk, Gtk, Pango

from pulse_task.core.task import Task, TaskStatus
from pulse_task.ui.countdown_widget import CountdownSize, CountdownStatus, CountdownWidget


class OverlayMode:
    """Overlay density mode constants."""

    NORMAL = "normal"
    COMPACT = "compact"
    ULTRACOMPACT = "ultracompact"


class CompactOverlay(Gtk.Window):
    """Always-on-top compact overlay window for active tasks.

    Features:
    - Three density modes (normal, compact, ultra-compact)
    - Draggable by mouse
    - Quick play/pause/complete actions
    - Mode switcher buttons
    - Keyboard toggle (Ctrl+O)
    """

    def __init__(
        self,
        on_start: Callable[[], None] | None = None,
        on_pause: Callable[[], None] | None = None,
        on_resume: Callable[[], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        # Store callbacks
        self.on_start = on_start
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_complete = on_complete
        self.on_close = on_close

        # State
        self._mode = OverlayMode.NORMAL
        self._task: Task | None = None
        self._drag_start_x = 0
        self._drag_start_y = 0

        # Configure window
        self.set_title("PulseTask Overlay")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_default_size(320, -1)

        # Set window type hint for overlay behavior
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        # Set up dragging
        self._drag_controller = Gtk.GestureDrag.new()
        self._drag_controller.connect("drag-begin", self._on_drag_begin)
        self._drag_controller.connect("drag-update", self._on_drag_update)
        self.add_controller(self._drag_controller)

        # Build initial UI
        self._build_ui()

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        self._mode = value
        self._build_ui()
        self._update_size()

    def update_task(self, task: Task | None) -> None:
        """Update the overlay with a new task."""
        self._task = task
        self._build_ui()
        self._update_size()

    def _update_size(self) -> None:
        """Update window size based on mode."""
        sizes = {
            OverlayMode.NORMAL: (320, -1),
            OverlayMode.COMPACT: (288, -1),
            OverlayMode.ULTRACOMPACT: (180, -1),
        }
        width, height = sizes.get(self._mode, (320, -1))
        self.set_default_size(width, height)

    def _build_ui(self) -> None:
        """Build the overlay UI based on current mode."""
        # Remove existing content
        child = self.get_child()
        if child:
            self.remove(child)

        if self._task is None:
            self._build_empty_state()
            return

        match self._mode:
            case OverlayMode.ULTRACOMPACT:
                self._build_ultracompact()
            case OverlayMode.COMPACT:
                self._build_compact()
            case _:
                self._build_normal()

    def _build_empty_state(self) -> None:
        """Build empty state when no task is active."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
        )
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(16)
        box.set_margin_end(16)

        label = Gtk.Label(label="No active task")
        label.add_css_class("dim-label")
        label.set_hexpand(True)
        box.append(label)

        close_btn = Gtk.Button()
        close_btn.add_css_class("flat")
        close_btn.set_child(Gtk.Image.new_from_icon_name("window-close-symbolic"))
        close_btn.connect("clicked", lambda btn: self._on_close_clicked())
        box.append(close_btn)

        self.set_child(box)

    def _build_ultracompact(self) -> None:
        """Build ultra-compact mode: just timer and play/pause."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.add_css_class("overlay")

        # Countdown widget (XS)
        self.countdown = CountdownWidget(
            size=CountdownSize.XS,
            show_progress=False,
        )
        self._update_countdown()
        box.append(self.countdown)

        # Play/Pause button
        play_pause_btn = self._create_play_pause_button()
        box.append(play_pause_btn)

        # Expand button
        expand_btn = Gtk.Button()
        expand_btn.add_css_class("flat")
        expand_btn.set_child(Gtk.Image.new_from_icon_name("zoom-expand-symbolic"))
        expand_btn.set_tooltip_text("Expand overlay")
        expand_btn.connect("clicked", lambda btn: setattr(self, "mode", OverlayMode.COMPACT))
        box.append(expand_btn)

        self.set_child(box)

    def _build_compact(self) -> None:
        """Build compact mode: title, timer, and controls."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.add_css_class("overlay")

        # Header row: title + buttons
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        # Title
        title_label = Gtk.Label(xalign=0, label=self._task.title)
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_hexpand(True)
        header.append(title_label)

        # Mode buttons
        minimize_btn = Gtk.Button()
        minimize_btn.add_css_class("flat")
        minimize_btn.set_child(Gtk.Image.new_from_icon_name("zoom-fit-best-symbolic"))
        minimize_btn.set_tooltip_text("Ultra-compact")
        minimize_btn.connect("clicked", lambda btn: setattr(self, "mode", OverlayMode.ULTRACOMPACT))
        header.append(minimize_btn)

        close_btn = Gtk.Button()
        close_btn.add_css_class("flat")
        close_btn.set_child(Gtk.Image.new_from_icon_name("window-close-symbolic"))
        close_btn.connect("clicked", lambda btn: self._on_close_clicked())
        header.append(close_btn)

        box.append(header)

        # Countdown widget (SM)
        self.countdown = CountdownWidget(
            size=CountdownSize.SM,
            show_progress=True,
        )
        self._update_countdown()
        box.append(self.countdown)

        # Controls row
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        play_pause_btn = self._create_play_pause_button()
        play_pause_btn.set_hexpand(True)
        controls.append(play_pause_btn)

        if self._task.status in {TaskStatus.RUNNING, TaskStatus.EXPIRED}:
            complete_btn = Gtk.Button(label="Done")
            complete_btn.add_css_class("btn-success")
            complete_btn.connect("clicked", lambda btn: self._on_complete_clicked())
            controls.append(complete_btn)

        box.append(controls)
        self.set_child(box)

    def _build_normal(self) -> None:
        """Build normal mode: full info with all controls."""
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
        )
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.add_css_class("overlay")

        # Header row
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        # Title
        title_label = Gtk.Label(xalign=0)
        title_label.set_markup(f"<b>{self._escape_markup(self._task.title)}</b>")
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_hexpand(True)
        header.append(title_label)

        # Mode buttons
        compact_btn = Gtk.Button()
        compact_btn.add_css_class("flat")
        compact_btn.set_child(Gtk.Image.new_from_icon_name("zoom-fit-best-symbolic"))
        compact_btn.set_tooltip_text("Compact mode")
        compact_btn.connect("clicked", lambda btn: setattr(self, "mode", OverlayMode.COMPACT))
        header.append(compact_btn)

        close_btn = Gtk.Button()
        close_btn.add_css_class("flat")
        close_btn.set_child(Gtk.Image.new_from_icon_name("window-close-symbolic"))
        close_btn.connect("clicked", lambda btn: self._on_close_clicked())
        header.append(close_btn)

        box.append(header)

        # Description (if exists)
        if self._task.description:
            desc_label = Gtk.Label(xalign=0, label=self._task.description)
            desc_label.add_css_class("dim-label")
            desc_label.set_ellipsize(Pango.EllipsizeMode.END)
            box.append(desc_label)

        # Countdown widget (MD)
        self.countdown = CountdownWidget(
            size=CountdownSize.MD,
            show_progress=True,
        )
        self._update_countdown()
        box.append(self.countdown)

        # Subtask progress (if applicable)
        if self._task.parent_task_id is None and self._task.subtasks:
            completed = sum(1 for st in self._task.subtasks if st.status == TaskStatus.COMPLETED)
            total = len(self._task.subtasks)

            subtask_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=8,
            )

            label = Gtk.Label(xalign=0, label="Steps:")
            label.add_css_class("dim-label")
            subtask_box.append(label)

            progress_label = Gtk.Label(
                xalign=0,
                label=f"{completed}/{total}",
            )
            progress_label.add_css_class("dim-label")
            subtask_box.append(progress_label)

            box.append(subtask_box)

        # Controls row
        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        play_pause_btn = self._create_play_pause_button()
        play_pause_btn.set_hexpand(True)
        controls.append(play_pause_btn)

        if self._task.status in {TaskStatus.RUNNING, TaskStatus.EXPIRED}:
            complete_btn = Gtk.Button(label="Done")
            complete_btn.add_css_class("btn-success")
            complete_btn.connect("clicked", lambda btn: self._on_complete_clicked())
            controls.append(complete_btn)

        box.append(controls)
        self.set_child(box)

    def _create_play_pause_button(self) -> Gtk.Button:
        """Create a play/pause button based on task status."""
        if self._task.status == TaskStatus.RUNNING:
            btn = Gtk.Button(label="Pause")
            btn.add_css_class("btn-secondary")
            btn.connect("clicked", lambda btn: self._on_pause_clicked())
        else:
            label = "Resume" if self._task.status == TaskStatus.PAUSED else "Start"
            btn = Gtk.Button(label=label)
            btn.add_css_class("btn-primary")
            btn.connect("clicked", lambda btn: self._on_start_clicked())
        return btn

    def _update_countdown(self) -> None:
        """Update countdown widget with current task data."""
        if self._task is None or not hasattr(self, "countdown"):
            return

        self.countdown.elapsed = self._task.duration_seconds - self._task.remaining_seconds
        self.countdown.duration = self._task.duration_seconds

        status_map = {
            TaskStatus.PENDING: CountdownStatus.PENDING,
            TaskStatus.RUNNING: CountdownStatus.RUNNING,
            TaskStatus.PAUSED: CountdownStatus.PAUSED,
            TaskStatus.EXPIRED: CountdownStatus.EXPIRED,
            TaskStatus.COMPLETED: CountdownStatus.COMPLETED,
        }
        self.countdown.status = status_map.get(self._task.status, CountdownStatus.PENDING)

    def _on_drag_begin(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle drag start."""
        self._drag_start_x = x
        self._drag_start_y = y

    def _on_drag_update(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle drag update - move the window."""
        root = self.get_root()
        if root is None:
            return

        # Calculate new position
        window_x = root.get_x() + (x - self._drag_start_x)
        window_y = root.get_y() + (y - self._drag_start_y)

        self.set_position(window_x, window_y)

    def _on_start_clicked(self) -> None:
        """Handle start/resume click."""
        if self._task.status == TaskStatus.PAUSED and self.on_resume:
            self.on_resume()
        elif self.on_start:
            self.on_start()

    def _on_pause_clicked(self) -> None:
        """Handle pause click."""
        if self.on_pause:
            self.on_pause()

    def _on_complete_clicked(self) -> None:
        """Handle complete click."""
        if self.on_complete:
            self.on_complete()

    def _on_close_clicked(self) -> None:
        """Handle close click."""
        self.set_visible(False)
        if self.on_close:
            self.on_close()

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
