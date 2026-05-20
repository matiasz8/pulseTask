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


def test_update_task_changes_title_description_and_duration(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Old title", 300, "Old")

    updated = service.update_task(
        task.id,
        title="New title",
        description="New description",
        duration_minutes=25,
    )

    assert updated.title == "New title"
    assert updated.description == "New description"
    assert updated.duration_seconds == 1500
    assert updated.remaining_seconds == 1500


def test_update_task_rejects_running_task(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Running", 300)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)

    try:
        service.update_task(
            task.id,
            title="Edited",
            description="Desc",
            duration_minutes=30,
        )
    except ValueError as exc:
        assert "Pause the task" in str(exc)
    else:
        raise AssertionError("Expected ValueError when editing a running task")


def test_archive_task_hides_from_default_listing(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Archive me", 300)

    service.archive_task(task.id)

    assert len(service.list_tasks()) == 0
    archived = service.list_archived_tasks()
    assert len(archived) == 1
    assert archived[0].status == TaskStatus.ARCHIVED


def test_delete_task_removes_entity(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Delete me", 300)

    service.delete_task(task.id)

    try:
        service.get_task(task.id)
    except ValueError as exc:
        assert "Task not found" in str(exc)
    else:
        raise AssertionError("Expected ValueError for deleted task")


def test_restore_task_snapshot_after_delete(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Recover me", 300)
    snapshot = service.get_task(task.id)

    service.delete_task(task.id)
    restored = service.restore_task_snapshot(snapshot)

    assert restored.id == task.id
    persisted = service.get_task(task.id)
    assert persisted.title == "Recover me"


def test_restore_task_snapshot_after_archive(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Archive recover", 300)
    snapshot = service.get_task(task.id)

    service.archive_task(task.id)
    service.restore_task_snapshot(snapshot)

    restored = service.get_task(task.id)
    assert restored.status == TaskStatus.PENDING
    assert len(service.list_archived_tasks()) == 0


def test_snooze_task_restarts_countdown(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    task = service.create_task("Snooze", 60)
    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(task.id, now=now)
    service.tick(now=now + timedelta(seconds=61))

    snoozed = service.snooze_task(task.id, minutes=5, now=now + timedelta(seconds=62))

    assert snoozed.status == TaskStatus.RUNNING
    assert snoozed.remaining_seconds == 300


def test_start_block_starts_first_subtask_by_sequence(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    parent = service.create_task("Morning block", 1200)
    child_2 = service.create_subtask(parent.id, "Second", 300, sequence_order=2)
    child_0 = service.create_subtask(parent.id, "First", 300, sequence_order=0)
    child_1 = service.create_subtask(parent.id, "Third", 300, sequence_order=1)

    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    started = service.start_block(parent.id, now=now)

    assert started.id == child_0.id
    assert started.status == TaskStatus.RUNNING
    listed = service.list_subtasks(parent.id)
    assert [task.id for task in listed] == [child_0.id, child_1.id, child_2.id]


def test_expired_subtask_autostarts_next_subtask(tmp_path: Path) -> None:
    service = _make_service(tmp_path)
    parent = service.create_task("Block", 1200)
    first = service.create_subtask(parent.id, "First", 60, sequence_order=0)
    second = service.create_subtask(parent.id, "Second", 60, sequence_order=1)

    now = datetime(2026, 5, 20, 12, 0, tzinfo=UTC)
    service.start_task(first.id, now=now)
    changed = service.tick(now=now + timedelta(seconds=61))

    first_after = service.get_task(first.id)
    second_after = service.get_task(second.id)
    assert first_after.status == TaskStatus.EXPIRED
    assert second_after.status == TaskStatus.RUNNING
    assert any(task.id == second.id and task.status == TaskStatus.RUNNING for task in changed)
