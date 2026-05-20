from datetime import UTC, datetime, timedelta
from pathlib import Path

from pulse_task.core.persistence import TaskRepository
from pulse_task.core.service import TaskService
from pulse_task.core.task import TaskStatus


def _make_service(tmp_path: Path) -> TaskService:
    repo = TaskRepository(tmp_path / "service.db")
    return TaskService(repository=repo)


def test_create_and_start_task(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Deploy", 900, "Release prod")

    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    started = service.start_task(task.id, now=now)

    assert started.status == TaskStatus.RUNNING
    assert started.target_at == now + timedelta(seconds=900)


def test_only_one_running_task_allowed(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    t1 = service.create_task("Task 1", 300)
    t2 = service.create_task("Task 2", 300)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)

    service.start_task(t1.id, now=now)

    try:
        service.start_task(t2.id, now=now)
    except ValueError as exc:
        assert "Only one running task" in str(exc)
    else:
        raise AssertionError("Expected ValueError when starting a second running task")


def test_tick_expires_running_task(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Email", 60)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)

    changed = service.tick(now=now + timedelta(seconds=61))

    assert len(changed) == 1
    expired = service.get_task(task.id)
    assert expired.status == TaskStatus.EXPIRED
    assert expired.remaining_seconds == 0


def test_recover_running_tasks_after_restart(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Deep work", 120)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)

    recovered = service.recover_running_tasks(now=now + timedelta(seconds=30))

    assert len(recovered) == 1
    persisted = service.get_task(task.id)
    assert persisted.status == TaskStatus.RUNNING
    assert persisted.remaining_seconds in {89, 90}
