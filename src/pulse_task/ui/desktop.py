from __future__ import annotations

# mypy: ignore-errors
from dataclasses import dataclass

from pulse_task.core.service import TaskService
from pulse_task.core.task import Task, TaskStatus


@dataclass(slots=True)
class RuntimeNotice:
    message: str
    is_error: bool = False


def launch_desktop_ui(service: TaskService) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, GLib, Gtk
    except Exception as exc:  # pragma: no cover - depends on local desktop setup
        print("GTK4/libadwaita is not available in this environment.")
        print("Install dependencies on Ubuntu:")
        print("  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1")
        print(f"Details: {exc}")
        return 1

    def format_seconds(total: int) -> str:
        minutes, seconds = divmod(max(0, total), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    class MainWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application, app_service: TaskService) -> None:
            super().__init__(application=app)
            self.service = app_service
            self.set_title("PulseTask")
            self.set_default_size(980, 620)

            self.notice = RuntimeNotice(message="Ready")

            root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            root.set_margin_top(16)
            root.set_margin_bottom(16)
            root.set_margin_start(16)
            root.set_margin_end(16)

            header = Gtk.HeaderBar()
            header.set_title_widget(Gtk.Label(label="PulseTask"))
            new_button = Gtk.Button(label="New task")
            new_button.connect("clicked", self._on_new_task_clicked)
            header.pack_end(new_button)
            root.append(header)

            self.active_label = Gtk.Label(xalign=0)
            self.active_label.set_markup("<b>No active task</b>")
            root.append(self.active_label)

            self.notice_label = Gtk.Label(xalign=0)
            root.append(self.notice_label)

            self.task_list = Gtk.ListBox()
            self.task_list.set_selection_mode(Gtk.SelectionMode.NONE)
            scroller = Gtk.ScrolledWindow()
            scroller.set_vexpand(True)
            scroller.set_child(self.task_list)
            root.append(scroller)

            self.set_content(root)
            self._refresh_view()

            GLib.timeout_add_seconds(1, self._on_timer_tick)

        def _on_timer_tick(self) -> bool:
            try:
                self.service.tick()
                self._refresh_view()
            except Exception as exc:  # pragma: no cover - UI safety
                self._set_notice(f"Tick error: {exc}", is_error=True)
            return True

        def _on_new_task_clicked(self, _button: Gtk.Button) -> None:
            dialog = Gtk.Dialog(title="Create task", transient_for=self, modal=True)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Create", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            title_entry = Gtk.Entry(placeholder_text="Task title")
            desc_entry = Gtk.Entry(placeholder_text="Description (optional)")
            duration = Gtk.SpinButton.new_with_range(60, 8 * 3600, 60)
            duration.set_value(20 * 60)

            box.append(Gtk.Label(label="Title", xalign=0))
            box.append(title_entry)
            box.append(Gtk.Label(label="Description", xalign=0))
            box.append(desc_entry)
            box.append(Gtk.Label(label="Duration (seconds)", xalign=0))
            box.append(duration)
            area.append(box)

            dialog.connect(
                "response",
                self._on_create_task_response,
                title_entry,
                desc_entry,
                duration,
            )
            dialog.present()

        def _on_create_task_response(
            self,
            dialog: Gtk.Dialog,
            response_id: int,
            title_entry: Gtk.Entry,
            desc_entry: Gtk.Entry,
            duration: Gtk.SpinButton,
        ) -> None:
            if response_id == Gtk.ResponseType.OK:
                title = title_entry.get_text().strip()
                if not title:
                    self._set_notice("Title is required", is_error=True)
                else:
                    try:
                        self.service.create_task(
                            title=title,
                            description=desc_entry.get_text().strip(),
                            duration_seconds=duration.get_value_as_int(),
                        )
                        self._set_notice("Task created")
                    except Exception as exc:
                        self._set_notice(f"Cannot create task: {exc}", is_error=True)
            dialog.close()
            self._refresh_view()

        def _set_notice(self, message: str, is_error: bool = False) -> None:
            self.notice = RuntimeNotice(message=message, is_error=is_error)
            color = "#cc0000" if is_error else "#6b7280"
            self.notice_label.set_markup(f"<span foreground='{color}'>{message}</span>")

        def _refresh_view(self) -> None:
            while True:
                child = self.task_list.get_first_child()
                if child is None:
                    break
                self.task_list.remove(child)

            tasks = self.service.list_tasks()
            running = next((task for task in tasks if task.status == TaskStatus.RUNNING), None)
            if running is None:
                self.active_label.set_markup("<b>No active task</b>")
            else:
                self.active_label.set_markup(
                    f"<b>Active:</b> {running.title} - {format_seconds(running.remaining_seconds)}"
                )

            for task in tasks:
                self.task_list.append(self._build_task_row(task))

        def _build_task_row(self, task: Task) -> Gtk.ListBoxRow:
            row = Gtk.ListBoxRow()
            wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            wrap.set_margin_top(10)
            wrap.set_margin_bottom(10)
            wrap.set_margin_start(10)
            wrap.set_margin_end(10)

            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            title = Gtk.Label(xalign=0)
            title.set_hexpand(True)
            title.set_markup(f"<b>{task.title}</b>")
            top.append(title)

            status = Gtk.Label(label=task.status.value.title())
            top.append(status)
            wrap.append(top)

            meta = Gtk.Label(
                xalign=0,
                label=(
                    f"Remaining: {format_seconds(task.remaining_seconds)} "
                    f"of {format_seconds(task.duration_seconds)}"
                ),
            )
            wrap.append(meta)

            actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            if task.status in {TaskStatus.PENDING, TaskStatus.PAUSED}:
                start_label = "Start" if task.status == TaskStatus.PENDING else "Resume"
                start_btn = Gtk.Button(label=start_label)
                start_btn.connect("clicked", self._on_start_resume_clicked, task.id)
                actions.append(start_btn)
            elif task.status == TaskStatus.RUNNING:
                pause_btn = Gtk.Button(label="Pause")
                pause_btn.connect("clicked", self._on_pause_clicked, task.id)
                actions.append(pause_btn)

            reset_btn = Gtk.Button(label="Reset")
            reset_btn.connect("clicked", self._on_reset_clicked, task.id)
            actions.append(reset_btn)

            wrap.append(actions)
            row.set_child(wrap)
            return row

        def _on_start_resume_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            task = self.service.get_task(task_id)
            try:
                if task.status == TaskStatus.PENDING:
                    self.service.start_task(task_id)
                else:
                    self.service.resume_task(task_id)
                self._set_notice("Task running")
            except Exception as exc:
                self._set_notice(f"Cannot start/resume: {exc}", is_error=True)
            self._refresh_view()

        def _on_pause_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            try:
                self.service.pause_task(task_id)
                self._set_notice("Task paused")
            except Exception as exc:
                self._set_notice(f"Cannot pause task: {exc}", is_error=True)
            self._refresh_view()

        def _on_reset_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            try:
                self.service.reset_task(task_id)
                self._set_notice("Task reset")
            except Exception as exc:
                self._set_notice(f"Cannot reset task: {exc}", is_error=True)
            self._refresh_view()

    class PulseTaskApplication(Adw.Application):
        def __init__(self, app_service: TaskService) -> None:
            super().__init__(application_id="com.matiasz8.pulsetask")
            self.app_service = app_service
            self.window: MainWindow | None = None

        def do_activate(self) -> None:
            if self.window is None:
                self.window = MainWindow(self, self.app_service)
            self.window.present()

    app = PulseTaskApplication(service)
    return int(app.run([]))
