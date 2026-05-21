from pulse_task.ui.desktop import (
    keyboard_shortcut_action,
    keyboard_shortcut_items,
    keyboard_shortcut_tooltip,
    make_icon_button,
    minimize_window_to_tray,
    restore_window_from_tray,
    should_minimize_to_tray,
    should_open_expired_dialog,
)


class _FakeWindow:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def set_visible(self, visible: bool) -> None:
        self.calls.append(f"visible:{visible}")

    def show(self) -> None:
        self.calls.append("show")

    def present(self) -> None:
        self.calls.append("present")

    def hide(self) -> None:
        self.calls.append("hide")


class _FakeImage:
    def __init__(self, icon_name: str) -> None:
        self.icon_name = icon_name


class _FakeButton:
    def __init__(self) -> None:
        self.css_classes: list[str] = []
        self.tooltip_text = ""
        self.child = None

    def add_css_class(self, css_class: str) -> None:
        self.css_classes.append(css_class)

    def set_tooltip_text(self, tooltip_text: str) -> None:
        self.tooltip_text = tooltip_text

    def set_child(self, child) -> None:
        self.child = child


class _FakeGtk:
    Button = _FakeButton

    class Image:
        @staticmethod
        def new_from_icon_name(icon_name: str) -> _FakeImage:
            return _FakeImage(icon_name)


def test_restore_window_from_tray_calls_show_then_present() -> None:
    window = _FakeWindow()

    restore_window_from_tray(window)

    assert window.calls == ["visible:True", "show", "present"]


def test_minimize_window_to_tray_calls_hide() -> None:
    window = _FakeWindow()

    minimize_window_to_tray(window)

    assert window.calls == ["visible:False", "hide"]


def test_should_minimize_to_tray_requires_tray_and_permissions() -> None:
    assert should_minimize_to_tray(object(), allow_close=False, close_to_tray=True) is True
    assert should_minimize_to_tray(None, allow_close=False, close_to_tray=True) is False
    assert should_minimize_to_tray(object(), allow_close=True, close_to_tray=True) is False
    assert should_minimize_to_tray(object(), allow_close=False, close_to_tray=False) is False


def test_should_open_expired_dialog_blocks_duplicates() -> None:
    open_ids = {"task-1"}

    assert should_open_expired_dialog(open_ids, "task-2") is True
    assert should_open_expired_dialog(open_ids, "task-1") is False


def test_make_icon_button_sets_icon_and_tooltip() -> None:
    button = make_icon_button(_FakeGtk, "user-trash-symbolic", "Delete")

    assert button.css_classes == ["flat"]
    assert button.tooltip_text == "Delete"
    assert isinstance(button.child, _FakeImage)
    assert button.child.icon_name == "user-trash-symbolic"


def test_keyboard_shortcut_action_maps_common_commands() -> None:
    assert keyboard_shortcut_action(True, False, "n") == "new_task"
    assert keyboard_shortcut_action(True, False, "z") == "undo"
    assert keyboard_shortcut_action(True, False, "comma") == "settings"
    assert keyboard_shortcut_action(True, True, "a") == "toggle_archived"
    assert keyboard_shortcut_action(False, False, "space") == "toggle_active"
    assert keyboard_shortcut_action(False, False, "x") is None


def test_keyboard_shortcut_items_lists_help_content() -> None:
    items = keyboard_shortcut_items()

    assert items == [
        ("Ctrl+N", "Create a new task"),
        ("Ctrl+Z", "Undo the last archive or delete action"),
        ("Ctrl+,", "Open Settings"),
        ("Ctrl+Shift+A", "Toggle archived tasks"),
        ("Space", "Start, pause, or resume the active task"),
    ]


def test_keyboard_shortcut_tooltip_includes_all_shortcuts() -> None:
    tooltip = keyboard_shortcut_tooltip()

    assert "Keyboard shortcuts:" in tooltip
    assert "Ctrl+N - Create a new task" in tooltip
    assert "Ctrl+Z - Undo the last archive or delete action" in tooltip
    assert "Ctrl+, - Open Settings" in tooltip
    assert "Ctrl+Shift+A - Toggle archived tasks" in tooltip
    assert "Space - Start, pause, or resume the active task" in tooltip
