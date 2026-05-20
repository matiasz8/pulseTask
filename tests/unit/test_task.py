from pulse_task.core.task import Task, TaskStatus


def test_task_defaults_remaining_to_duration() -> None:
    task = Task(title="Deploy", duration_seconds=900)
    assert task.remaining_seconds == 900
    assert task.status == TaskStatus.PENDING


def test_task_rejects_invalid_duration() -> None:
    try:
        Task(title="Invalid", duration_seconds=0)
    except ValueError as exc:
        assert "duration_seconds" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid duration")
