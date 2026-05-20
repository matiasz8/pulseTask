from datetime import UTC, datetime, timedelta

from pulse_task.core.task import Task, TaskStatus
from pulse_task.core.timer import TimerEngine


def test_start_sets_target_timestamp() -> None:
    engine = TimerEngine()
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    task = Task(title="Email", duration_seconds=1200)

    engine.start(task, now=now)

    assert task.status == TaskStatus.RUNNING
    assert task.target_at == now + timedelta(seconds=1200)


def test_pause_and_resume_keep_remaining_time() -> None:
    engine = TimerEngine()
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    task = Task(title="Study", duration_seconds=1800)
    engine.start(task, now=now)

    engine.pause(task, now=now + timedelta(seconds=300))
    remaining_after_pause = task.remaining_seconds

    engine.resume(task, now=now + timedelta(seconds=700))

    assert task.status == TaskStatus.RUNNING
    assert task.remaining_seconds == remaining_after_pause


def test_refresh_expires_task_when_target_reached() -> None:
    engine = TimerEngine()
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    task = Task(title="Deploy", duration_seconds=60)
    engine.start(task, now=now)

    engine.refresh(task, now=now + timedelta(seconds=61))

    assert task.status == TaskStatus.EXPIRED
    assert task.remaining_seconds == 0
    assert task.finished_at is not None
