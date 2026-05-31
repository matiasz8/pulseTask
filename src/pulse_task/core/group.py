"""Group task execution module.

Provides data models for executing multiple tasks as a cohesive group
with shared time budget and auto-advancement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class GroupStatus(StrEnum):
    """Task group execution state."""

    IDLE = "idle"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(slots=True)
class TaskGroup:
    """Represents a group of tasks executed sequentially with shared time budget."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # Core execution properties
    status: GroupStatus = GroupStatus.IDLE
    task_ids: list[str] = field(default_factory=list)
    total_time_seconds: int = 3600
    elapsed_time_seconds: int = 0
    paused_time_seconds: int = 0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    archived_at: datetime | None = None

    # Execution state
    current_task_index: int = 0
    paused_at: datetime | None = None

    # Statistics
    tasks_completed: int = 0
    tasks_skipped: int = 0

    def __post_init__(self) -> None:
        """Validate group on creation."""
        if not self.name:
            raise ValueError("name is required")
        if self.total_time_seconds <= 0:
            raise ValueError("total_time_seconds must be > 0")
        if not self.task_ids:
            raise ValueError("task_ids cannot be empty")

    def is_active(self) -> bool:
        """Is group currently executing?"""
        return self.status == GroupStatus.EXECUTING

    def is_complete(self) -> bool:
        """Have all tasks been processed (completed or skipped)?"""
        return self.tasks_completed + self.tasks_skipped == len(self.task_ids)

    def time_remaining_seconds(self) -> int:
        """Time remaining for entire group."""
        return max(0, self.total_time_seconds - self.elapsed_time_seconds)

    def current_task_id(self) -> str | None:
        """Get ID of currently executing task."""
        if 0 <= self.current_task_index < len(self.task_ids):
            return self.task_ids[self.current_task_index]
        return None

    def progress_percent(self) -> int:
        """Group progress as percentage (0-100)."""
        if not self.task_ids:
            return 0
        total_tasks = len(self.task_ids)
        completed_pct = int(((self.tasks_completed + self.tasks_skipped) / total_tasks) * 100)
        return min(100, completed_pct)

    def has_next_task(self) -> bool:
        """Are there more tasks to execute?"""
        return self.current_task_index < len(self.task_ids)


@dataclass(slots=True)
class GroupMember:
    """Metadata for a task within a group context."""

    group_id: str
    task_id: str
    order: int

    time_allocated: int = 0
    time_spent: int = 0
    completed_at: datetime | None = None
    skipped_at: datetime | None = None
