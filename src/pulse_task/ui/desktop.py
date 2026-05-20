from __future__ import annotations

# mypy: ignore-errors
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from pulse_task.core.preferences import PreferencesRepository, UserPreferences
from pulse_task.core.service import TaskService
from pulse_task.core.task import Task, TaskStatus
from pulse_task.system.tray import build_tray_controller


@dataclass(slots=True)
class RuntimeNotice:
    message: str
    is_error: bool = False


@dataclass(slots=True)
class UndoAction:
    action_type: str
    task: Task


def launch_desktop_ui(
    service: TaskService,
    preferences_repo: PreferencesRepository,
    preferences: UserPreferences,
) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gdk, GLib, Gtk
    except Exception as exc:  # pragma: no cover - depends on local desktop setup
        print("GTK4/libadwaita is not available in this environment.")
        print("Install dependencies on Ubuntu:")
        print("  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin")
        print("Then recreate the uv venv with system packages:")
        print("  rm -rf .venv && make venv && make sync && make doctor-gtk")
        print(f"Details: {exc}")
        return 1

    app_icon_name = "com.matiasz8.pulsetask"
    if hasattr(Gtk.Window, "set_default_icon_name"):
        Gtk.Window.set_default_icon_name(app_icon_name)

    def format_seconds(total: int) -> str:
        minutes, seconds = divmod(max(0, total), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def format_minutes(total_seconds: int) -> int:
        return max(1, total_seconds // 60)

    def format_minutes_human(total_minutes: int) -> str:
        if total_minutes >= 60:
            hours = total_minutes // 60
            rem = total_minutes % 60
            if rem == 0:
                return f"{hours}h"
            return f"{hours}h and {rem} min"
        return f"{total_minutes} min"

    class MainWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application, app_service: TaskService) -> None:
            super().__init__(application=app)
            self.service = app_service
            self.preferences_repo = preferences_repo
            self.preferences = preferences
            self.show_archived = self.preferences.show_archived_by_default
            self._allow_close = False
            self.tray_controller = None
            self.set_title("PulseTask")
            self.set_default_size(980, 620)
            if hasattr(self, "set_icon_name"):
                self.set_icon_name(app_icon_name)

            self.notice = RuntimeNotice(message="Ready")
            self.last_undo_action: UndoAction | None = None
            self.undo_expires_at = 0.0
            self._install_css()

            root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            root.set_margin_top(16)
            root.set_margin_bottom(16)
            root.set_margin_start(16)
            root.set_margin_end(16)

            header = Gtk.HeaderBar()
            header.add_css_class("flat")
            title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            icon_path = Path(__file__).resolve().parent / "assets" / f"{app_icon_name}.svg"
            if icon_path.exists():
                app_icon = Gtk.Image.new_from_file(str(icon_path))
                app_icon.set_pixel_size(18)
                title_box.append(app_icon)
            title_box.append(Gtk.Label(label="PulseTask"))
            header.set_title_widget(title_box)

            archived_button = Gtk.Button(label="Show archived: Off")
            archived_button.add_css_class("pill")
            archived_button.connect("clicked", self._on_toggle_archived_clicked)
            self.archived_button = archived_button

            settings_button = Gtk.Button(label="Settings")
            settings_button.add_css_class("pill")
            settings_button.connect("clicked", self._on_settings_clicked)

            undo_button = Gtk.Button(label="Undo")
            undo_button.add_css_class("pill")
            undo_button.set_sensitive(False)
            undo_button.connect("clicked", self._on_undo_clicked)
            self.undo_button = undo_button

            new_button = Gtk.Button(label="New task")
            new_button.add_css_class("suggested-action")
            new_button.connect("clicked", self._on_new_task_clicked)
            root.append(header)

            controls_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            controls_row.append(archived_button)
            controls_row.append(settings_button)
            controls_row.append(undo_button)
            controls_row.append(new_button)
            root.append(controls_row)

            self.active_label = Gtk.Label(xalign=0)
            self.active_label.add_css_class("active-label")
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
            self._setup_keyboard_shortcuts()
            self._sync_preferences_to_runtime()
            self._refresh_view()
            self.tray_controller = self._setup_tray()
            self.connect("close-request", self._on_close_request)

            GLib.timeout_add_seconds(1, self._on_timer_tick)

        def _setup_tray(self):
            controller = build_tray_controller(
                on_open=self._open_from_tray,
                on_toggle=self._toggle_active_task,
                on_reset=self._reset_active_task,
                on_quit=self._quit_from_tray,
                format_seconds=format_seconds,
            )
            if controller is None:
                self._set_notice("Tray indicator unavailable in this desktop session.")
            return controller

        def _open_from_tray(self) -> None:
            self.present()

        def _quit_from_tray(self) -> None:
            self._allow_close = True
            app = self.get_application()
            if app is not None:
                app.quit()

        def _on_close_request(self, _window) -> bool:
            if (
                self.tray_controller is None
                or self._allow_close
                or not self.preferences.close_to_tray
            ):
                return False
            self.hide()
            self._set_notice("PulseTask minimized to tray")
            return True

        def _sync_preferences_to_runtime(self) -> None:
            self.service.set_strong_final_sound(self.preferences.strong_final_sound)
            state_label = "On" if self.show_archived else "Off"
            self.archived_button.set_label(f"Show archived: {state_label}")

        def _save_preferences(self) -> None:
            self.preferences.show_archived_by_default = self.show_archived
            self.preferences = self.preferences.normalized()
            self.preferences_repo.save(self.preferences)
            self._sync_preferences_to_runtime()

        def _reset_active_task(self) -> None:
            tasks = self._visible_tasks()
            candidate = next(
                (task for task in tasks if task.status == TaskStatus.RUNNING),
                None,
            )
            if candidate is None:
                candidate = next(
                    (
                        task
                        for task in tasks
                        if task.status in {TaskStatus.PAUSED, TaskStatus.PENDING}
                    ),
                    None,
                )
            if candidate is None:
                return
            try:
                self.service.reset_task(candidate.id)
                self._set_notice("Task reset")
            except Exception as exc:
                self._set_notice(f"Cannot reset task: {exc}", is_error=True)
            self._refresh_view()

        def _install_css(self) -> None:
            css = """
            .task-card {
                background: alpha(@theme_fg_color, 0.04);
                border-radius: 12px;
                border: 1px solid alpha(@theme_fg_color, 0.12);
                padding: 4px;
            }
            .active-label {
                font-size: 1.05rem;
            }
            .status-running {
                color: #1f7a1f;
                font-weight: 600;
            }
            .status-paused {
                color: #c06b00;
                font-weight: 600;
            }
            .status-expired {
                color: #bb1e1e;
                font-weight: 700;
            }
            .status-archived {
                color: #5c6370;
            }
            .pill {
                border-radius: 999px;
            }
            """
            provider = Gtk.CssProvider()
            provider.load_from_data(css.encode("utf-8"))
            Gtk.StyleContext.add_provider_for_display(
                self.get_display(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

        def _setup_keyboard_shortcuts(self) -> None:
            key_controller = Gtk.EventControllerKey.new()
            key_controller.connect("key-pressed", self._on_key_pressed)
            self.add_controller(key_controller)

        def _on_key_pressed(
            self,
            _controller: Gtk.EventControllerKey,
            keyval: int,
            _keycode: int,
            state: Gdk.ModifierType,
        ) -> bool:
            ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
            if ctrl and keyval in {Gdk.KEY_n, Gdk.KEY_N}:
                self._on_new_task_clicked(Gtk.Button())
                return True
            if ctrl and keyval in {Gdk.KEY_z, Gdk.KEY_Z}:
                self._on_undo_clicked(Gtk.Button())
                return True
            if keyval == Gdk.KEY_space:
                self._toggle_active_task()
                return True
            return False

        def _set_undo_action(self, action_type: str, task: Task) -> None:
            self.last_undo_action = UndoAction(action_type=action_type, task=task)
            self.undo_expires_at = monotonic() + 12
            self.undo_button.set_sensitive(True)
            self._set_notice(f"Task {action_type}d. Undo available for 12s (Ctrl+Z)")

        def _clear_undo_action(self) -> None:
            self.last_undo_action = None
            self.undo_expires_at = 0.0
            self.undo_button.set_sensitive(False)

        def _expire_undo_if_needed(self) -> None:
            if self.last_undo_action is None:
                return
            if monotonic() >= self.undo_expires_at:
                self._clear_undo_action()
                self._set_notice("Undo window expired")

        def _on_undo_clicked(self, _button: Gtk.Button) -> None:
            if self.last_undo_action is None:
                return
            self._expire_undo_if_needed()
            if self.last_undo_action is None:
                return
            try:
                self.service.restore_task_snapshot(self.last_undo_action.task)
                label = self.last_undo_action.action_type
                self._set_notice(f"Undo completed: {label}")
                self._clear_undo_action()
            except Exception as exc:
                self._set_notice(f"Cannot undo action: {exc}", is_error=True)
            self._refresh_view()

        def _toggle_active_task(self) -> None:
            tasks = self._visible_tasks()
            running = next((task for task in tasks if task.status == TaskStatus.RUNNING), None)
            try:
                if running is not None:
                    self.service.pause_task(running.id)
                    self._set_notice("Task paused")
                else:
                    resumable = next(
                        (
                            task
                            for task in tasks
                            if task.status in {TaskStatus.PAUSED, TaskStatus.PENDING}
                        ),
                        None,
                    )
                    if resumable is None:
                        return
                    if resumable.status == TaskStatus.PAUSED:
                        self.service.resume_task(resumable.id)
                    else:
                        self.service.start_task(resumable.id)
                    self._set_notice("Task running")
            except Exception as exc:
                self._set_notice(f"Cannot toggle task: {exc}", is_error=True)
            self._refresh_view()

        def _visible_tasks(self) -> list[Task]:
            tasks = self.service.list_tasks()
            if self.show_archived:
                tasks.extend(self.service.list_archived_tasks())
            return tasks

        def _on_timer_tick(self) -> bool:
            try:
                self._expire_undo_if_needed()
                changed = self.service.tick()
                for task in changed:
                    if task.status == TaskStatus.EXPIRED:
                        self._open_expired_dialog(task)
                self._refresh_view()
            except Exception as exc:  # pragma: no cover - UI safety
                self._set_notice(f"Tick error: {exc}", is_error=True)
            return True

        def _on_toggle_archived_clicked(self, _button: Gtk.Button) -> None:
            self.show_archived = not self.show_archived
            state_label = "On" if self.show_archived else "Off"
            self.archived_button.set_label(f"Show archived: {state_label}")
            self._save_preferences()
            self._refresh_view()

        def _on_new_task_clicked(self, _button: Gtk.Button) -> None:
            dialog = Gtk.Dialog(title="Create task", transient_for=self, modal=True)
            dialog.set_default_size(580, 340)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Create", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(20)
            box.set_margin_bottom(20)
            box.set_margin_start(20)
            box.set_margin_end(20)

            title_entry = Gtk.Entry(placeholder_text="Task title")
            desc_entry = Gtk.Entry(placeholder_text="Description (optional)")
            duration_adjustment = Gtk.Adjustment(
                value=self.preferences.default_duration_minutes,
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
            duration_scale.set_hexpand(True)
            duration_scale.set_draw_value(False)
            minus_btn = Gtk.Button(label="-")
            plus_btn = Gtk.Button(label="+")
            duration_label = Gtk.Label(
                label=format_minutes_human(self.preferences.default_duration_minutes),
                xalign=0,
            )
            duration_scale.connect(
                "value-changed",
                self._on_minutes_scale_changed,
                duration_label,
            )
            minus_btn.connect("clicked", self._on_minutes_minus_clicked, duration_scale)
            plus_btn.connect("clicked", self._on_minutes_plus_clicked, duration_scale)

            minutes_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            minutes_row.append(minus_btn)
            minutes_row.append(duration_scale)
            minutes_row.append(plus_btn)

            box.append(Gtk.Label(label="Title", xalign=0))
            box.append(title_entry)
            box.append(Gtk.Label(label="Description", xalign=0))
            box.append(desc_entry)
            box.append(Gtk.Label(label="Duration (minutes)", xalign=0))
            box.append(minutes_row)
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

        def _on_minutes_scale_changed(
            self,
            scale: Gtk.Scale,
            label: Gtk.Label,
        ) -> None:
            minutes = int(scale.get_value())
            label.set_text(format_minutes_human(minutes))

        def _on_minutes_minus_clicked(self, _button: Gtk.Button, scale: Gtk.Scale) -> None:
            current = int(scale.get_value())
            scale.set_value(max(1, current - 1))

        def _on_minutes_plus_clicked(self, _button: Gtk.Button, scale: Gtk.Scale) -> None:
            current = int(scale.get_value())
            scale.set_value(min(480, current + 1))

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

        def _open_expired_dialog(self, task: Task) -> None:
            dialog = Gtk.Dialog(title="Task expired", transient_for=self, modal=True)
            dialog.set_default_size(500, 230)
            dialog.add_button("Close", Gtk.ResponseType.CLOSE)
            dialog.add_button("Snooze 1m", 101)
            dialog.add_button("Snooze 5m", 105)

            area = dialog.get_content_area()
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            content.set_margin_top(24)
            content.set_margin_bottom(24)
            content.set_margin_start(24)
            content.set_margin_end(24)

            title = Gtk.Label(
                label=f"{task.title} reached its deadline.",
                xalign=0,
            )
            title.set_wrap(True)
            detail = Gtk.Label(
                label="Choose a snooze interval to restart a short countdown.",
                xalign=0,
            )
            detail.set_wrap(True)
            content.append(title)
            content.append(detail)
            area.append(content)

            dialog.connect("response", self._on_expired_response, task.id)
            dialog.present()

        def _on_expired_response(self, dialog: Gtk.Dialog, response_id: int, task_id: str) -> None:
            snooze_map = {
                101: 1,
                105: 5,
            }
            if response_id in snooze_map:
                try:
                    minutes = snooze_map[response_id]
                    self.service.snooze_task(task_id, minutes=minutes)
                    self._set_notice(f"Task snoozed for {minutes} minutes")
                except Exception as exc:
                    self._set_notice(f"Cannot snooze task: {exc}", is_error=True)
            dialog.close()
            self._refresh_view()

        def _on_settings_clicked(self, _button: Gtk.Button) -> None:
            dialog = Gtk.Dialog(title="Settings", transient_for=self, modal=True)
            dialog.set_default_size(520, 300)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Save", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            box.set_margin_top(20)
            box.set_margin_bottom(20)
            box.set_margin_start(20)
            box.set_margin_end(20)

            duration_spin = Gtk.SpinButton.new_with_range(1, 480, 1)
            duration_spin.set_value(self.preferences.default_duration_minutes)

            show_archived_check = Gtk.CheckButton(label="Show archived tasks by default")
            show_archived_check.set_active(self.preferences.show_archived_by_default)

            strong_sound_check = Gtk.CheckButton(label="Use stronger final alert sound")
            strong_sound_check.set_active(self.preferences.strong_final_sound)

            close_to_tray_check = Gtk.CheckButton(label="Close to tray when available")
            close_to_tray_check.set_active(self.preferences.close_to_tray)

            box.append(Gtk.Label(label="Default task duration (minutes)", xalign=0))
            box.append(duration_spin)
            box.append(show_archived_check)
            box.append(strong_sound_check)
            box.append(close_to_tray_check)
            area.append(box)

            dialog.connect(
                "response",
                self._on_settings_response,
                duration_spin,
                show_archived_check,
                strong_sound_check,
                close_to_tray_check,
            )
            dialog.present()

        def _on_settings_response(
            self,
            dialog: Gtk.Dialog,
            response_id: int,
            duration_spin: Gtk.SpinButton,
            show_archived_check: Gtk.CheckButton,
            strong_sound_check: Gtk.CheckButton,
            close_to_tray_check: Gtk.CheckButton,
        ) -> None:
            if response_id == Gtk.ResponseType.OK:
                self.preferences.default_duration_minutes = duration_spin.get_value_as_int()
                self.preferences.show_archived_by_default = show_archived_check.get_active()
                self.preferences.strong_final_sound = strong_sound_check.get_active()
                self.preferences.close_to_tray = close_to_tray_check.get_active()
                self.show_archived = self.preferences.show_archived_by_default
                self._save_preferences()
                self._set_notice("Settings saved")
            dialog.close()
            self._refresh_view()

        def _open_edit_task_dialog(self, task: Task) -> None:
            dialog = Gtk.Dialog(title="Edit task", transient_for=self, modal=True)
            dialog.set_default_size(580, 340)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Save", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(20)
            box.set_margin_bottom(20)
            box.set_margin_start(20)
            box.set_margin_end(20)

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
            duration_scale.set_hexpand(True)
            duration_scale.set_draw_value(False)
            minus_btn = Gtk.Button(label="-")
            plus_btn = Gtk.Button(label="+")
            duration_label = Gtk.Label(label=format_minutes_human(minutes_value), xalign=0)
            duration_scale.connect(
                "value-changed",
                self._on_minutes_scale_changed,
                duration_label,
            )
            minus_btn.connect("clicked", self._on_minutes_minus_clicked, duration_scale)
            plus_btn.connect("clicked", self._on_minutes_plus_clicked, duration_scale)

            minutes_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            minutes_row.append(minus_btn)
            minutes_row.append(duration_scale)
            minutes_row.append(plus_btn)

            box.append(Gtk.Label(label="Title", xalign=0))
            box.append(title_entry)
            box.append(Gtk.Label(label="Description", xalign=0))
            box.append(desc_entry)
            box.append(Gtk.Label(label="Duration (minutes)", xalign=0))
            box.append(minutes_row)
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

            tasks = self._visible_tasks()
            running = next((task for task in tasks if task.status == TaskStatus.RUNNING), None)
            if running is None:
                self.active_label.set_markup("<b>No active task</b>")
                self.set_title("PulseTask")
            else:
                self.active_label.set_markup(
                    f"<b>Active:</b> {running.title} - {format_seconds(running.remaining_seconds)}"
                )
                self.set_title(f"[{format_seconds(running.remaining_seconds)}] PulseTask")

            for task in tasks:
                self.task_list.append(self._build_task_row(task))

            if self.tray_controller is not None:
                self.tray_controller.update(tasks)

        def _build_task_row(self, task: Task) -> Gtk.ListBoxRow:
            row = Gtk.ListBoxRow()
            wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            wrap.add_css_class("task-card")
            wrap.set_margin_top(8)
            wrap.set_margin_bottom(8)
            wrap.set_margin_start(8)
            wrap.set_margin_end(8)

            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            title = Gtk.Label(xalign=0)
            title.set_hexpand(True)
            title.set_markup(f"<b>{task.title}</b>")
            top.append(title)

            status = Gtk.Label(label=task.status.value.title())
            if task.status == TaskStatus.RUNNING:
                status.add_css_class("status-running")
            elif task.status == TaskStatus.PAUSED:
                status.add_css_class("status-paused")
            elif task.status == TaskStatus.EXPIRED:
                status.add_css_class("status-expired")
            elif task.status == TaskStatus.ARCHIVED:
                status.add_css_class("status-archived")
            top.append(status)
            wrap.append(top)

            meta = Gtk.Label(
                xalign=0,
                label=(
                    f"Remaining: {format_seconds(task.remaining_seconds)} "
                    f"of {format_seconds(task.duration_seconds)} "
                    f"({format_minutes_human(format_minutes(task.duration_seconds))})"
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

            if task.status != TaskStatus.ARCHIVED:
                reset_btn = Gtk.Button(label="Reset")
                reset_btn.connect("clicked", self._on_reset_clicked, task.id)
                actions.append(reset_btn)

                edit_btn = Gtk.Button(label="Edit")
                edit_btn.connect("clicked", self._on_edit_clicked, task.id)
                actions.append(edit_btn)

                archive_btn = Gtk.Button(label="Archive")
                archive_btn.connect("clicked", self._on_archive_clicked, task.id)
                actions.append(archive_btn)
            else:
                restore_btn = Gtk.Button(label="Unarchive")
                restore_btn.connect("clicked", self._on_unarchive_clicked, task.id)
                actions.append(restore_btn)

            delete_btn = Gtk.Button(label="Delete")
            delete_btn.connect("clicked", self._on_delete_clicked, task.id)
            actions.append(delete_btn)

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

        def _on_archive_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            try:
                snapshot = self.service.get_task(task_id)
                self.service.archive_task(task_id)
                self._set_undo_action("archive", snapshot)
            except Exception as exc:
                self._set_notice(f"Cannot archive task: {exc}", is_error=True)
            self._refresh_view()

        def _on_unarchive_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            try:
                task = self.service.get_task(task_id)
                self.service.update_task(
                    task_id,
                    title=task.title,
                    description=task.description,
                    duration_minutes=format_minutes(task.duration_seconds),
                )
                self._set_notice("Task unarchived")
            except Exception as exc:
                self._set_notice(f"Cannot unarchive task: {exc}", is_error=True)
            self._refresh_view()

        def _on_delete_clicked(self, _button: Gtk.Button, task_id: str) -> None:
            dialog = Gtk.Dialog(title="Delete task", transient_for=self, modal=True)
            dialog.set_default_size(420, 180)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Delete", Gtk.ResponseType.OK)

            area = dialog.get_content_area()
            label = Gtk.Label(
                xalign=0,
                label="Delete this task permanently? This action cannot be undone.",
            )
            label.set_margin_top(16)
            label.set_margin_bottom(16)
            label.set_margin_start(16)
            label.set_margin_end(16)
            label.set_wrap(True)
            area.append(label)

            dialog.connect("response", self._on_delete_response, task_id)
            dialog.present()

        def _on_delete_response(self, dialog: Gtk.Dialog, response_id: int, task_id: str) -> None:
            if response_id == Gtk.ResponseType.OK:
                try:
                    snapshot = self.service.get_task(task_id)
                    self.service.delete_task(task_id)
                    self._set_undo_action("delete", snapshot)
                except Exception as exc:
                    self._set_notice(f"Cannot delete task: {exc}", is_error=True)
            dialog.close()
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
