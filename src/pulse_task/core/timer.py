from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pulse_task.core.task import Task, TaskStatus


class TimerEngine:
    """Absolute timestamp-based timer engine.

    Remaining time is always derived from target timestamps to avoid drift.
    """

    def start(self, task: Task, now: datetime | None = None) -> Task:
        if task.is_terminal():
            raise ValueError("Cannot start a terminal task")
        ts = now or datetime.now(UTC)
        task.started_at = ts
        task.target_at = ts + timedelta(seconds=task.remaining_seconds)
        task.paused_at = None
        task.finished_at = None
        task.status = TaskStatus.RUNNING
        return task

    def pause(self, task: Task, now: datetime | None = None) -> Task:
        if task.status != TaskStatus.RUNNING or task.target_at is None:
            raise ValueError("Task must be running to pause")
        ts = now or datetime.now(UTC)
        task.remaining_seconds = max(0, int((task.target_at - ts).total_seconds()))
        task.paused_at = ts
        task.target_at = None
        task.status = TaskStatus.PAUSED
        return task

    def resume(self, task: Task, now: datetime | None = None) -> Task:
        if task.status != TaskStatus.PAUSED:
            raise ValueError("Task must be paused to resume")
        return self.start(task, now=now)

    def reset(self, task: Task) -> Task:
        task.remaining_seconds = task.duration_seconds
        task.status = TaskStatus.PENDING
        task.started_at = None
        task.target_at = None
        task.paused_at = None
        task.finished_at = None
        return task

    def refresh(self, task: Task, now: datetime | None = None) -> Task:
        if task.status != TaskStatus.RUNNING or task.target_at is None:
            return task

        ts = now or datetime.now(UTC)
        remaining = int((task.target_at - ts).total_seconds())
        if remaining <= 0:
            task.remaining_seconds = 0
            task.finished_at = ts
            task.status = TaskStatus.EXPIRED
            task.target_at = None
            return task

        task.remaining_seconds = remaining
        return task

    def recover_running_task(self, task: Task, now: datetime | None = None) -> Task:
        """Recover running tasks after app/system restart.

        Assumes target_at was persisted. If target is in the past, mark as expired.
        """
        return self.refresh(task, now=now)
