from __future__ import annotations

from datetime import datetime

from pulse_task.core.alerts import AlertEvent, AlertManager
from pulse_task.core.persistence import TaskRepository
from pulse_task.core.task import Task, TaskStatus
from pulse_task.core.timer import TimerEngine


class TaskService:
    """Coordinates task CRUD, timer transitions, and persistence."""

    def __init__(
        self,
        repository: TaskRepository,
        timer_engine: TimerEngine | None = None,
        alert_manager: AlertManager | None = None,
    ) -> None:
        self.repository = repository
        self.timer_engine = timer_engine or TimerEngine()
        self.alert_manager = alert_manager or AlertManager()

    def create_task(self, title: str, duration_seconds: int, description: str = "") -> Task:
        task = Task(
            title=title.strip(),
            description=description.strip(),
            duration_seconds=duration_seconds,
        )
        self.repository.upsert(task)
        return task

    def get_task(self, task_id: str) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise ValueError(f"Task not found: {task_id}")
        return task

    def list_tasks(self) -> list[Task]:
        return [task for task in self.repository.list_all() if task.status != TaskStatus.ARCHIVED]

    def list_archived_tasks(self) -> list[Task]:
        return [task for task in self.repository.list_all() if task.status == TaskStatus.ARCHIVED]

    def start_task(self, task_id: str, now: datetime | None = None) -> Task:
        self._ensure_no_other_running(task_id)
        task = self.get_task(task_id)
        started = self.timer_engine.start(task, now=now)
        self.repository.upsert(started)
        self.alert_manager.notify_task_started(started.title, started.remaining_seconds)
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
        self.alert_manager.notify_task_started(resumed.title, resumed.remaining_seconds)
        return resumed

    def update_task(
        self,
        task_id: str,
        *,
        title: str,
        description: str,
        duration_minutes: int,
    ) -> Task:
        task = self.get_task(task_id)
        if task.status == TaskStatus.RUNNING:
            raise ValueError("Pause the task before editing")

        task.title = title.strip()
        if not task.title:
            raise ValueError("Title is required")
        task.description = description.strip()
        duration_seconds = duration_minutes * 60
        task.duration_seconds = duration_seconds
        task.remaining_seconds = duration_seconds
        if task.status in {TaskStatus.COMPLETED, TaskStatus.EXPIRED, TaskStatus.ARCHIVED}:
            task.status = TaskStatus.PENDING
            task.finished_at = None

        self.repository.upsert(task)
        return task

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

    def archive_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task.status == TaskStatus.RUNNING:
            raise ValueError("Pause the task before archiving")
        task.status = TaskStatus.ARCHIVED
        task.target_at = None
        self.repository.upsert(task)
        return task

    def delete_task(self, task_id: str) -> None:
        self.repository.delete(task_id)

    def snooze_task(self, task_id: str, minutes: int, now: datetime | None = None) -> Task:
        if minutes <= 0:
            raise ValueError("Snooze minutes must be > 0")
        self._ensure_no_other_running(task_id)
        task = self.get_task(task_id)
        task.remaining_seconds = minutes * 60
        task.status = TaskStatus.PAUSED
        task.finished_at = None
        task.target_at = None
        snoozed = self.timer_engine.resume(task, now=now)
        self.repository.upsert(snoozed)
        self.alert_manager.notify_task_started(snoozed.title, snoozed.remaining_seconds)
        return snoozed

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
                if before_status == TaskStatus.RUNNING and refreshed.status == TaskStatus.EXPIRED:
                    self.alert_manager.alert_task_expired(
                        AlertEvent(task_id=refreshed.id, title=refreshed.title)
                    )
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
