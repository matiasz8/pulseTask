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
        print("  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin")
        print("Then recreate the uv venv with system packages:")
        print("  rm -rf .venv && make venv && make sync && make doctor-gtk")
        print(f"Details: {exc}")
        return 1

    def format_seconds(total: int) -> str:
        minutes, seconds = divmod(max(0, total), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def format_minutes(total_seconds: int) -> int:
        return max(1, total_seconds // 60)

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
            duration_adjustment = Gtk.Adjustment(
                value=20,
                lower=1,
                upper=480,
                step_increment=1,
                page_increment=10,
                page_size=0,
            )
            duration_scale = Gtk.Scale(
                orientation=Gtk.Orientation.HORIZONTAL,
                adjustment=duration_adjustment,
            )
            duration_scale.set_draw_value(False)
            duration_label = Gtk.Label(label="20 min", xalign=0)
            duration_scale.connect("value-changed", self._on_minutes_scale_changed, duration_label)

            box.append(Gtk.Label(label="Title", xalign=0))
            box.append(title_entry)
            box.append(Gtk.Label(label="Description", xalign=0))
            box.append(desc_entry)
            box.append(Gtk.Label(label="Duration (minutes)", xalign=0))
            box.append(duration_scale)
            box.append(duration_label)
            area.append(box)

            dialog.connect(
                "response",
                self._on_create_task_response,
                title_entry,
                desc_entry,
                duration_scale,
            )
            dialog.present()

        def _on_minutes_scale_changed(self, scale: Gtk.Scale, label: Gtk.Label) -> None:
            label.set_text(f"{int(scale.get_value())} min")

        def _on_create_task_response(
            self,
            dialog: Gtk.Dialog,
            response_id: int,
            title_entry: Gtk.Entry,
            desc_entry: Gtk.Entry,
            duration_scale: Gtk.Scale,
        ) -> None:
            if response_id == Gtk.ResponseType.OK:
                title = title_entry.get_text().strip()
                if not title:
                    self._set_notice("Title is required", is_error=True)
                else:
                    try:
                        minutes = int(duration_scale.get_value())
                        self.service.create_task(
                            title=title,
                            description=desc_entry.get_text().strip(),
                            duration_seconds=minutes * 60,
                        )
                        self._set_notice("Task created")
                    except Exception as exc:
                        self._set_notice(f"Cannot create task: {exc}", is_error=True)
            dialog.close()
            self._refresh_view()

        def _open_edit_task_dialog(self, task: Task) -> None:
            dialog = Gtk.Dialog(title="Edit task", transient_for=self, modal=True)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Save", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            title_entry = Gtk.Entry()
            title_entry.set_text(task.title)
            desc_entry = Gtk.Entry()
            desc_entry.set_text(task.description)

            minutes_value = format_minutes(task.duration_seconds)
            duration_adjustment = Gtk.Adjustment(
                value=minutes_value,
                lower=1,
                upper=480,
                step_increment=1,
                page_increment=10,
                page_size=0,
            )
            duration_scale = Gtk.Scale(
                orientation=Gtk.Orientation.HORIZONTAL,
                adjustment=duration_adjustment,
            )
            duration_scale.set_draw_value(False)
            duration_label = Gtk.Label(label=f"{minutes_value} min", xalign=0)
            duration_scale.connect("value-changed", self._on_minutes_scale_changed, duration_label)

            box.append(Gtk.Label(label="Title", xalign=0))
            box.append(title_entry)
            box.append(Gtk.Label(label="Description", xalign=0))
            box.append(desc_entry)
            box.append(Gtk.Label(label="Duration (minutes)", xalign=0))
            box.append(duration_scale)
            box.append(duration_label)
            area.append(box)

            dialog.connect(
                "response",
                self._on_edit_task_response,
                task.id,
                title_entry,
                desc_entry,
                duration_scale,
            )
            dialog.present()

        def _on_edit_task_response(
            self,
            dialog: Gtk.Dialog,
            response_id: int,
            task_id: str,
            title_entry: Gtk.Entry,
            desc_entry: Gtk.Entry,
            duration_scale: Gtk.Scale,
        ) -> None:
            if response_id == Gtk.ResponseType.OK:
                try:
                    self.service.update_task(
                        task_id,
                        title=title_entry.get_text(),
                        description=desc_entry.get_text(),
                        duration_minutes=int(duration_scale.get_value()),
                    )
                    self._set_notice("Task updated")
                except Exception as exc:
                    self._set_notice(f"Cannot update task: {exc}", is_error=True)
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
                    f"of {format_seconds(task.duration_seconds)} "
                    f"({format_minutes(task.duration_seconds)} min)"
                ),
            )
            wrap.append(meta)

            if task.description:
                desc = Gtk.Label(xalign=0, label=task.description)
                wrap.append(desc)

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

            edit_btn = Gtk.Button(label="Edit")
            edit_btn.connect("clicked", self._on_edit_clicked, task.id)
            actions.append(edit_btn)

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

        def _on_edit_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            task = self.service.get_task(task_id)
            self._open_edit_task_dialog(task)

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
