from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from pulse_task.core.task import Task, TaskStatus


def _to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _from_iso(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


class TaskRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._ensure_parent_dir()
        self._init_db()

    def _ensure_parent_dir(self) -> None:
        if self.db_path == ":memory:":
            return
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    remaining_seconds INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    target_at TEXT,
                    paused_at TEXT,
                    finished_at TEXT
                )
                """
            )

    def upsert(self, task: Task) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, description, duration_seconds, remaining_seconds, status,
                    created_at, started_at, target_at, paused_at, finished_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    duration_seconds=excluded.duration_seconds,
                    remaining_seconds=excluded.remaining_seconds,
                    status=excluded.status,
                    created_at=excluded.created_at,
                    started_at=excluded.started_at,
                    target_at=excluded.target_at,
                    paused_at=excluded.paused_at,
                    finished_at=excluded.finished_at
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.duration_seconds,
                    task.remaining_seconds,
                    task.status.value,
                    _to_iso(task.created_at),
                    _to_iso(task.started_at),
                    _to_iso(task.target_at),
                    _to_iso(task.paused_at),
                    _to_iso(task.finished_at),
                ),
            )

    def get(self, task_id: str) -> Task | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                return None
            return self._row_to_task(row)

    def list_all(self) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
            return [self._row_to_task(row) for row in rows]

    def delete(self, task_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            duration_seconds=row["duration_seconds"],
            remaining_seconds=row["remaining_seconds"],
            status=TaskStatus(row["status"]),
            created_at=_from_iso(row["created_at"]) or datetime.now(UTC),
            started_at=_from_iso(row["started_at"]),
            target_at=_from_iso(row["target_at"]),
            paused_at=_from_iso(row["paused_at"]),
            finished_at=_from_iso(row["finished_at"]),
        )
