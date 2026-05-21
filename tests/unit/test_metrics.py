from datetime import UTC, datetime, timedelta
from pathlib import Path

from pulse_task.core.alerts import AlertManager
from pulse_task.core.metrics import LocalMetrics
from pulse_task.core.persistence import TaskRepository
from pulse_task.core.service import TaskService


class _FakeAudio:
    def play_alert(self) -> None:
        return

    def play_countdown_cue(self) -> None:
        return


class _FakeNotify:
    def send(self, title: str, body: str) -> None:
        _ = (title, body)


class _FakeMetrics:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    def increment(self, metric_name: str, amount: int = 1) -> None:
        self.counts[metric_name] = self.counts.get(metric_name, 0) + amount


def test_local_metrics_persist_counters(tmp_path: Path) -> None:
    metrics_path = tmp_path / "metrics.json"
    metrics = LocalMetrics(metrics_path)

    metrics.increment("tasks_created")
    metrics.increment("tasks_created")
    metrics.increment("tasks_started")

    reloaded = LocalMetrics(metrics_path)

    assert reloaded.snapshot() == {"tasks_created": 2, "tasks_started": 1}


def test_service_emits_local_observability_metrics(tmp_path: Path) -> None:
    repo = TaskRepository(tmp_path / "metrics-service.db")
    fake_metrics = _FakeMetrics()
    alerts = AlertManager(
        audio_backend=_FakeAudio(),
        notification_backend=_FakeNotify(),
        debounce_seconds=0,
        notifications_enabled=False,
    )
    service = TaskService(repository=repo, alert_manager=alerts, metrics=fake_metrics)

    parent = service.create_task("Block", 120)
    child = service.create_subtask(parent.id, "Child", 60)
    now = datetime(2026, 5, 21, 12, 0, tzinfo=UTC)
    service.start_task(child.id, now=now)
    service.pause_task(child.id, now=now + timedelta(seconds=10))
    service.resume_task(child.id, now=now + timedelta(seconds=20))
    service.tick(now=now + timedelta(seconds=90))
    service.reset_task(parent.id)
    service.update_task(parent.id, title="Block v2", description="", duration_minutes=3)
    service.archive_task(parent.id)
    service.restore_task_snapshot(parent)
    service.delete_task(parent.id)

    assert fake_metrics.counts["tasks_created"] == 1
    assert fake_metrics.counts["subtasks_created"] == 1
    assert fake_metrics.counts["tasks_started"] == 1
    assert fake_metrics.counts["tasks_paused"] == 1
    assert fake_metrics.counts["tasks_resumed"] == 1
    assert fake_metrics.counts["tasks_expired"] == 1
    assert fake_metrics.counts["tasks_reset"] == 1
    assert fake_metrics.counts["tasks_updated"] == 1
    assert fake_metrics.counts["tasks_archived"] == 1
    assert fake_metrics.counts["tasks_restored"] == 1
    assert fake_metrics.counts["tasks_deleted"] == 1
