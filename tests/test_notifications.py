"""Unit tests for desktop notification formatting and callbacks."""

from __future__ import annotations

import types

import pytest

from pulse_task.system import notifications as notifications_module
from pulse_task.system.notifications import NotificationManager


class FakeVariant:
    def __init__(self, _signature: str, value: object) -> None:
        self.value = value

    def unpack(self) -> object:
        return self.value


class FakeBus:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.subscriptions: dict[str, object] = {}
        self._next_id = 1

    def call_sync(self, *_args: object) -> FakeVariant:
        self.calls.append({"method": _args[3], "parameters": _args[4]})
        notification_id = self._next_id
        self._next_id += 1
        return FakeVariant("(u)", (notification_id,))

    def signal_subscribe(self, *_args: object) -> None:
        self.subscriptions[str(_args[2])] = _args[6]


class FakeSettings:
    def __init__(self, values: dict[str, object] | None = None) -> None:
        self.values = values or {}

    def get_boolean(self, key: str) -> bool:
        return bool(self.values[key])

    def get_int(self, key: str) -> int:
        return int(self.values[key])


@pytest.fixture
def fake_bus(monkeypatch: pytest.MonkeyPatch) -> FakeBus:
    bus = FakeBus()
    fake_glib = types.SimpleNamespace(Variant=FakeVariant, VariantType=lambda signature: signature)
    fake_gio = types.SimpleNamespace(
        DBusCallFlags=types.SimpleNamespace(NONE=0),
        DBusSignalFlags=types.SimpleNamespace(NONE=0),
        BusType=types.SimpleNamespace(SESSION=0),
        bus_get_sync=lambda *_args: bus,
    )
    monkeypatch.setattr(notifications_module, "GLib", fake_glib)
    monkeypatch.setattr(notifications_module, "Gio", fake_gio)
    return bus


def test_send_task_expired_formats_dbus_payload(fake_bus: FakeBus) -> None:
    manager = NotificationManager(settings=FakeSettings(), bus=fake_bus)

    manager.send_task_expired("Write tests")

    parameters = fake_bus.calls[0]["parameters"].unpack()
    assert parameters[0] == "PulseTask"
    assert parameters[3] == "Task expired"
    assert parameters[4] == "Write tests"
    assert parameters[5][:4] == ["snooze", "Snooze 5m", "start-next", "Start next"]
    assert parameters[6]["desktop-entry"].unpack() == "org.gnome.Pulse"
    assert parameters[7] == 10000


@pytest.mark.parametrize(
    ("task_name", "expected"),
    [
        ("", "Untitled task"),
        ("Ship <v0.3.0> & celebrate", "Ship <v0.3.0> & celebrate"),
        ("x" * 90, f"{'x' * 77}..."),
    ],
)
def test_send_time_warning_handles_task_name_edge_cases(
    fake_bus: FakeBus,
    task_name: str,
    expected: str,
) -> None:
    manager = NotificationManager(settings=FakeSettings(), bus=fake_bus)

    manager.send_time_warning(task_name, 299)

    parameters = fake_bus.calls[-1]["parameters"].unpack()
    assert parameters[3] == "5 minutes remaining"
    assert parameters[4] == expected
    assert parameters[7] == 5000


def test_action_invoked_runs_registered_callback(fake_bus: FakeBus) -> None:
    called: list[str] = []
    manager = NotificationManager(settings=FakeSettings(), bus=fake_bus)
    notification_id = manager.send_task_expired(
        "Review PR",
        on_snooze=lambda: called.append("snooze"),
        on_start_next=lambda: called.append("next"),
    )

    fake_bus.subscriptions["ActionInvoked"](
        None,
        None,
        None,
        None,
        None,
        None,
        FakeVariant("(us)", (notification_id, "snooze")),
    )

    assert called == ["snooze"]


def test_send_focus_lost_uses_short_timeout(fake_bus: FakeBus) -> None:
    settings = FakeSettings({"notification-timeout": 10000})
    manager = NotificationManager(settings=settings, bus=fake_bus)

    manager.send_focus_lost("Deep work")

    parameters = fake_bus.calls[0]["parameters"].unpack()
    assert parameters[3] == "Window focus lost"
    assert parameters[4] == "Deep work auto-paused after the window lost focus."
    assert parameters[7] == 3000


def test_send_returns_none_when_notifications_disabled(fake_bus: FakeBus) -> None:
    manager = NotificationManager(
        settings=FakeSettings({"notification-enabled": False, "notifications-enabled": True}),
        bus=fake_bus,
    )

    result = manager.send_task_expired("Blocked")

    assert result is None
    assert fake_bus.calls == []
