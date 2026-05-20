from pulse_task.core.task import Task, TaskStatus
from pulse_task.system.tray import TrayCapabilities, _choose_toggle_label


def test_tray_capabilities_dataclass_defaults() -> None:
    caps = TrayCapabilities(available=False, reason="missing")
    assert caps.available is False
    assert caps.reason == "missing"


def test_choose_toggle_label_prefers_running() -> None:
    tasks = [
        Task(title="A", duration_seconds=60, status=TaskStatus.RUNNING),
        Task(title="B", duration_seconds=60, status=TaskStatus.PAUSED),
    ]
    assert _choose_toggle_label(tasks) == "Pause active"


def test_choose_toggle_label_for_paused_task() -> None:
    tasks = [Task(title="A", duration_seconds=60, status=TaskStatus.PAUSED)]
    assert _choose_toggle_label(tasks) == "Resume next"


def test_choose_toggle_label_for_pending_task() -> None:
    tasks = [Task(title="A", duration_seconds=60, status=TaskStatus.PENDING)]
    assert _choose_toggle_label(tasks) == "Start next"


def test_choose_toggle_label_when_no_candidates() -> None:
    tasks = [Task(title="A", duration_seconds=60, status=TaskStatus.ARCHIVED)]
    assert _choose_toggle_label(tasks) == "Start/Pause"
