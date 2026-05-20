from pathlib import Path

from pulse_task.core.persistence import TaskRepository
from pulse_task.core.task import Task


def test_upsert_and_get_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "tasks.db"
    repo = TaskRepository(db_path)

    task = Task(title="Write docs", description="README", duration_seconds=600)
    repo.upsert(task)

    stored = repo.get(task.id)
    assert stored is not None
    assert stored.title == "Write docs"
    assert stored.description == "README"


def test_list_all_returns_saved_tasks(tmp_path: Path) -> None:
    db_path = tmp_path / "tasks.db"
    repo = TaskRepository(db_path)

    repo.upsert(Task(title="Task A", duration_seconds=60))
    repo.upsert(Task(title="Task B", duration_seconds=120))

    items = repo.list_all()
    assert len(items) == 2
