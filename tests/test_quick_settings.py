"""Tests for the PulseTask Quick Settings widget."""

from __future__ import annotations

import pytest

pytest.importorskip("gi")

from pulse_task.core.group_service import GroupService
from pulse_task.core.persistence import Database
from pulse_task.dbus.status import StatusInterface
from pulse_task.system.quick_settings import QuickSettingsWidget


class FakeSettings:
    def __init__(self) -> None:
        self.values = {"show-quick-settings": True, "last-quick-settings-position": 0}
        self._handlers: dict[int, tuple[str, object]] = {}
        self._next_id = 1

    def get_boolean(self, key: str) -> bool:
        return bool(self.values.get(key, False))

    def get_int(self, key: str) -> int:
        return int(self.values.get(key, 0))

    def set_boolean(self, key: str, value: bool) -> None:
        self.values[key] = value
        self._emit(f"changed::{key}", key)

    def set_int(self, key: str, value: int) -> None:
        self.values[key] = value

    def set_string(self, key: str, value: str) -> None:
        self.values[key] = value

    def connect(self, signal: str, callback: object) -> int:
        handler_id = self._next_id
        self._next_id += 1
        self._handlers[handler_id] = (signal, callback)
        return handler_id

    def disconnect(self, handler_id: int) -> None:
        self._handlers.pop(handler_id, None)

    def _emit(self, signal: str, key: str) -> None:
        for registered_signal, callback in self._handlers.values():
            if registered_signal == signal:
                callback(self, key)


@pytest.fixture
def service() -> GroupService:
    return GroupService(Database(":memory:"))


@pytest.fixture
def widget(service: GroupService) -> QuickSettingsWidget:
    settings = FakeSettings()
    status = StatusInterface(service, settings=settings)
    widget = QuickSettingsWidget(service, status, settings=settings)
    widget._install_styles = lambda: None
    return widget


def test_widget_creation_and_settings_binding(widget: QuickSettingsWidget) -> None:
    assert widget.get_title() == "PulseTask"
    assert widget.status_label.get_label() == "Idle"
    assert widget.time_label.get_label() == "00:00"
    assert widget.pause_button.get_sensitive() is False

    widget.settings.set_boolean("show-quick-settings", False)
    assert widget.get_visible() is False
    widget.remember_position(3)
    assert widget.position == 3


def test_widget_reacts_to_realtime_updates(
    service: GroupService,
    widget: QuickSettingsWidget,
) -> None:
    group = service.create_group("Deep Focus", ["task-a", "task-b"], total_time_seconds=600)
    service.start_group_execution(group.id)
    service.update_group_elapsed_time(group.id, 5)

    widget.status_interface.set_active_group(group.id)
    assert widget.status_label.get_label() == "Running"
    assert widget.get_subtitle() == "Deep Focus"
    assert widget.time_label.get_label() == "09:55"


def test_pause_resume_button_callback(service: GroupService, widget: QuickSettingsWidget) -> None:
    group = service.create_group("Toggle Group", ["task-a"], total_time_seconds=120)
    service.start_group_execution(group.id)
    widget.status_interface.set_active_group(group.id)

    widget.pause_button.emit("clicked")
    assert service.get_group(group.id).status.value == "paused"

    widget.pause_button.emit("clicked")
    assert service.get_group(group.id).status.value == "executing"


def test_state_transitions(service: GroupService, widget: QuickSettingsWidget) -> None:
    group = service.create_group("Transitions", ["task-a"], total_time_seconds=90)
    service.start_group_execution(group.id)
    widget.status_interface.set_active_group(group.id)
    assert widget.status_label.get_label() == "Running"

    service.pause_group_execution(group.id)
    widget.status_interface.refresh(force=True)
    assert widget.status_label.get_label() == "Paused"

    service.resume_group_execution(group.id)
    widget.status_interface.refresh(force=True)
    assert widget.status_label.get_label() == "Running"

    service.advance_to_next_task(group.id)
    widget.status_interface.clear_active_group()
    assert widget.status_label.get_label() == "Idle"
    assert widget.time_label.get_label() == "00:00"
