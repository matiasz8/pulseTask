from datetime import UTC, datetime, timedelta
from pathlib import Path

from pulse_task.core.alerts import AlertManager
from pulse_task.core.persistence import TaskRepository
from pulse_task.core.service import TaskService


class _FakeAudio:
    def __init__(self) -> None:
        self.calls = 0
        self.cue_calls = 0

    def play_alert(self) -> None:
        self.calls += 1

    def play_countdown_cue(self) -> None:
        self.cue_calls += 1


class _FakeNotify:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def send(self, title: str, body: str) -> None:
        self.calls.append((title, body))


def test_service_tick_triggers_alert_on_expiration(tmp_path: Path) -> None:
    repo = TaskRepository(tmp_path / "alerts.db")
    audio = _FakeAudio()
    notify = _FakeNotify()
    alerts = AlertManager(audio_backend=audio, notification_backend=notify, debounce_seconds=0)
    service = TaskService(repository=repo, alert_manager=alerts)

    task = service.create_task("Release", 60)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)

    service.tick(now=now + timedelta(seconds=61))

    assert audio.calls == 1
    assert len(notify.calls) == 2
    assert notify.calls[0][0] == "Task started"
    assert notify.calls[1][0] == "Task expired"


def test_service_tick_triggers_last_three_seconds_cues(tmp_path: Path) -> None:
    repo = TaskRepository(tmp_path / "alerts-cue.db")
    audio = _FakeAudio()
    notify = _FakeNotify()
    alerts = AlertManager(audio_backend=audio, notification_backend=notify, debounce_seconds=0)
    service = TaskService(repository=repo, alert_manager=alerts)

    task = service.create_task("Cue", 7)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)

    for sec in [1, 2, 3, 4, 5, 6]:
        service.tick(now=now + timedelta(seconds=sec))

    assert audio.cue_calls == 3
