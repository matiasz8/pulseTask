from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ARCHIVED = "archived"


@dataclass(slots=True)
class Task:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    duration_seconds: int = 0
    remaining_seconds: int = -1
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    target_at: datetime | None = None
    paused_at: datetime | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be > 0")
        if self.remaining_seconds == -1:
            self.remaining_seconds = self.duration_seconds
        if self.remaining_seconds < 0:
            raise ValueError("remaining_seconds cannot be negative")

    def is_terminal(self) -> bool:
        return self.status in {TaskStatus.COMPLETED, TaskStatus.EXPIRED, TaskStatus.ARCHIVED}
