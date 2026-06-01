"""Tests for GNOME global shortcuts."""

from __future__ import annotations

import types

from pulse_task.system import shortcuts as shortcuts_module
from pulse_task.system.shortcuts import DEFAULT_SHORTCUTS, GlobalShortcuts


class FakeVariant:
    def __init__(self, _signature: str, value: object) -> None:
        self.value = value

    def unpack(self) -> object:
        return self.value


class FakeBus:
    def __init__(self) -> None:
        self.grabs: list[str] = []
        self.ungrabs: list[int] = []
        self.callback = None

    def call_sync(self, *_args: object) -> FakeVariant:
        method, parameters = _args[3], _args[4].unpack()
        if method == "GrabAccelerator":
            self.grabs.append(parameters[0])
            return FakeVariant("(u)", (len(self.grabs),))
        self.ungrabs.append(int(parameters[0]))
        return FakeVariant("(b)", (True,))

    def signal_subscribe(self, *_args: object) -> int:
        self.callback = _args[6]
        return 7

    def signal_unsubscribe(self, _subscription_id: int) -> None:
        self.callback = None


class FakeSettings:
    def __init__(self, enabled: bool = True, **overrides: object) -> None:
        self.values = {
            "global-shortcuts-enabled": enabled,
            "shortcut-pause-resume": DEFAULT_SHORTCUTS["pause-resume"],
            "shortcut-new-task": DEFAULT_SHORTCUTS["new-task"],
            "shortcut-show-stats": DEFAULT_SHORTCUTS["show-stats"],
            "shortcut-bring-window": DEFAULT_SHORTCUTS["bring-window"],
            **overrides,
        }

    def get_boolean(self, key: str) -> bool:
        return bool(self.values[key])

    def get_string(self, key: str) -> str:
        return str(self.values[key])


def test_parse_shortcut_accepts_valid_accelerators() -> None:
    assert GlobalShortcuts.parse_shortcut("<Super>alt+p") == ("super", "alt", "p")
    assert GlobalShortcuts.parse_shortcut("<Primary><Shift>comma") == (
        "primary",
        "shift",
        "comma",
    )
    assert GlobalShortcuts.parse_shortcut("broken+") is None


def test_all_shortcuts_dispatch_registered_handlers(monkeypatch) -> None:
    bus, triggered = FakeBus(), []
    monkeypatch.setattr(
        shortcuts_module,
        "GLib",
        types.SimpleNamespace(Variant=FakeVariant, VariantType=lambda value: value),
    )
    monkeypatch.setattr(
        shortcuts_module,
        "Gio",
        types.SimpleNamespace(
            DBusCallFlags=types.SimpleNamespace(NONE=0),
            DBusSignalFlags=types.SimpleNamespace(NONE=0),
        ),
    )
    shortcuts = GlobalShortcuts(
        settings=FakeSettings(),
        bus=bus,
        on_pause_resume=lambda: triggered.append("pause-resume"),
        on_new_task=lambda: triggered.append("new-task"),
        on_show_stats=lambda: triggered.append("show-stats"),
        on_bring_window=lambda: triggered.append("bring-window"),
    )

    assert shortcuts.register_shortcuts() is True
    for action_id in range(1, 5):
        bus.callback(None, None, None, None, None, None, FakeVariant("(uu)", (action_id, 0)))
    shortcuts.unregister_shortcuts()

    assert triggered == ["pause-resume", "new-task", "show-stats", "bring-window"]
    assert bus.ungrabs == [1, 2, 3, 4]


def test_custom_overrides_and_invalid_values_use_expected_bindings(monkeypatch) -> None:
    bus = FakeBus()
    monkeypatch.setattr(
        shortcuts_module,
        "GLib",
        types.SimpleNamespace(Variant=FakeVariant, VariantType=lambda value: value),
    )
    monkeypatch.setattr(
        shortcuts_module,
        "Gio",
        types.SimpleNamespace(
            DBusCallFlags=types.SimpleNamespace(NONE=0),
            DBusSignalFlags=types.SimpleNamespace(NONE=0),
        ),
    )
    shortcuts = GlobalShortcuts(
        settings=FakeSettings(
            **{
                "shortcut-pause-resume": "<Super>shift+p",
                "shortcut-new-task": "oops!",
            }
        ),
        bus=bus,
    )

    shortcuts.register_shortcuts()

    assert bus.grabs[0] == "<Super>shift+p"
    assert bus.grabs[1] == DEFAULT_SHORTCUTS["new-task"]


def test_disabled_or_unavailable_shortcuts_fail_gracefully() -> None:
    disabled = GlobalShortcuts(settings=FakeSettings(enabled=False), bus=FakeBus())
    unavailable = GlobalShortcuts(settings=FakeSettings(), bus=None)

    assert disabled.register_shortcuts() is False
    assert unavailable.register_shortcuts() is False
