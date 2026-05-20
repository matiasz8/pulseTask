from __future__ import annotations

from datetime import datetime

from pulse_task.core.persistence import TaskRepository
from pulse_task.core.task import Task, TaskStatus
from pulse_task.core.timer import TimerEngine


class TaskService:
    """Coordinates task CRUD, timer transitions, and persistence."""

    def __init__(self, repository: TaskRepository, timer_engine: TimerEngine | None = None) -> None:
        self.repository = repository
        self.timer_engine = timer_engine or TimerEngine()

    def create_task(self, title: str, duration_seconds: int, description: str = "") -> Task:
        task = Task(title=title.strip(), description=description.strip(), duration_seconds=duration_seconds)
        self.repository.upsert(task)
        return task

    def get_task(self, task_id: str) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise ValueError(f"Task not found: {task_id}")
        return task

    def list_tasks(self) -> list[Task]:
        return self.repository.list_all()

    def start_task(self, task_id: str, now: datetime | None = None) -> Task:
        self._ensure_no_other_running(task_id)
        task = self.get_task(task_id)
        started = self.timer_engine.start(task, now=now)
        self.repository.upsert(started)
        return started

    def pause_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        paused = self.timer_engine.pause(task, now=now)
        self.repository.upsert(paused)
        return paused

    def resume_task(self, task_id: str, now: datetime | None = None) -> Task:
        self._ensure_no_other_running(task_id)
        task = self.get_task(task_id)
        resumed = self.timer_engine.resume(task, now=now)
        self.repository.upsert(resumed)
        return resumed

    def reset_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        reset = self.timer_engine.reset(task)
        self.repository.upsert(reset)
        return reset

    def complete_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        task.status = TaskStatus.COMPLETED
        task.remaining_seconds = 0
        task.target_at = None
        task.finished_at = now
        self.repository.upsert(task)
        return task

    def tick(self, now: datetime | None = None) -> list[Task]:
        changed: list[Task] = []
        for task in self.repository.list_all():
            if task.status != TaskStatus.RUNNING:
                continue
            before_remaining = task.remaining_seconds
            before_status = task.status
            refreshed = self.timer_engine.refresh(task, now=now)
            if refreshed.remaining_seconds != before_remaining or refreshed.status != before_status:
                self.repository.upsert(refreshed)
                changed.append(refreshed)
        return changed

    def recover_running_tasks(self, now: datetime | None = None) -> list[Task]:
        recovered: list[Task] = []
        for task in self.repository.list_all():
            if task.status != TaskStatus.RUNNING:
                continue
            refreshed = self.timer_engine.recover_running_task(task, now=now)
            self.repository.upsert(refreshed)
            recovered.append(refreshed)
        return recovered

    def _ensure_no_other_running(self, selected_task_id: str) -> None:
        for existing in self.repository.list_all():
            if existing.id != selected_task_id and existing.status == TaskStatus.RUNNING:
                raise ValueError("Only one running task is allowed at a time")
