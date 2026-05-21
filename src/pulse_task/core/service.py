from __future__ import annotations

from datetime import datetime

from pulse_task.core.alerts import AlertEvent, AlertManager
from pulse_task.core.metrics import MetricsSink, NoOpMetrics
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
        metrics: MetricsSink | None = None,
    ) -> None:
        self.repository = repository
        self.timer_engine = timer_engine or TimerEngine()
        self.alert_manager = alert_manager or AlertManager()
        self.metrics = metrics or NoOpMetrics()

    def create_task(self, title: str, duration_seconds: int, description: str = "") -> Task:
        task = Task(
            title=title.strip(),
            description=description.strip(),
            duration_seconds=duration_seconds,
        )
        self.repository.upsert(task)
        self._increment_metric("tasks_created")
        return task

    def create_subtask(
        self,
        parent_task_id: str,
        title: str,
        duration_seconds: int,
        description: str = "",
        sequence_order: int | None = None,
    ) -> Task:
        self.get_task(parent_task_id)
        if sequence_order is None:
            sequence_order = self._next_sequence_order(parent_task_id)
        task = Task(
            parent_task_id=parent_task_id,
            sequence_order=sequence_order,
            title=title.strip(),
            description=description.strip(),
            duration_seconds=duration_seconds,
        )
        self.repository.upsert(task)
        self._increment_metric("subtasks_created")
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

    def list_subtasks(self, parent_task_id: str) -> list[Task]:
        siblings = [
            task
            for task in self.repository.list_all()
            if task.parent_task_id == parent_task_id and task.status != TaskStatus.ARCHIVED
        ]
        return sorted(siblings, key=self._task_sequence_sort_key)

    def get_block_progress(self, parent_task_id: str) -> tuple[int, int]:
        subtasks = self.list_subtasks(parent_task_id)
        total = len(subtasks)
        completed = len(
            [
                task
                for task in subtasks
                if task.status in {TaskStatus.COMPLETED, TaskStatus.EXPIRED}
            ]
        )
        return completed, total

    def reorder_subtask(self, task_id: str, direction: int) -> Task:
        if direction not in {-1, 1}:
            raise ValueError("direction must be -1 or 1")
        task = self.get_task(task_id)
        if task.parent_task_id is None:
            raise ValueError("Only subtasks can be reordered")

        siblings = self.list_subtasks(task.parent_task_id)
        index = next((i for i, item in enumerate(siblings) if item.id == task_id), None)
        if index is None:
            raise ValueError("Subtask not found in block")

        swap_index = index + direction
        if swap_index < 0 or swap_index >= len(siblings):
            return task

        current = siblings[index]
        other = siblings[swap_index]
        current_order = current.sequence_order
        other_order = other.sequence_order

        if current_order is None:
            current_order = index
        if other_order is None:
            other_order = swap_index

        current.sequence_order = other_order
        other.sequence_order = current_order
        self.repository.upsert(current)
        self.repository.upsert(other)
        self._increment_metric("subtasks_reordered")
        return current

    def start_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        self._ensure_no_other_running(task.id)
        started = self.timer_engine.start(task, now=now)
        self.repository.upsert(started)
        self.alert_manager.clear_countdown_cues(started.id)
        self.alert_manager.notify_task_started(started.title, started.remaining_seconds)
        self._increment_metric("tasks_started")
        return started

    def start_block(self, parent_task_id: str, now: datetime | None = None) -> Task:
        parent = self.get_task(parent_task_id)
        if parent.status == TaskStatus.RUNNING:
            return parent
        if parent.status == TaskStatus.PENDING:
            return self.start_task(parent_task_id, now=now)
        if parent.status == TaskStatus.PAUSED:
            return self.resume_task(parent_task_id, now=now)

        subtasks = self.list_subtasks(parent_task_id)
        candidate = next(
            (
                task
                for task in subtasks
                if task.status in {TaskStatus.PENDING, TaskStatus.PAUSED}
            ),
            None,
        )
        if candidate is None:
            raise ValueError("No pending subtasks available to start")
        if candidate.status == TaskStatus.PAUSED:
            return self.resume_task(candidate.id, now=now)
        return self.start_task(candidate.id, now=now)

    def pause_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        paused = self.timer_engine.pause(task, now=now)
        self.repository.upsert(paused)
        self.alert_manager.clear_countdown_cues(paused.id)
        self._increment_metric("tasks_paused")
        return paused

    def resume_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        self._ensure_no_other_running(task.id)
        resumed = self.timer_engine.resume(task, now=now)
        self.repository.upsert(resumed)
        self.alert_manager.clear_countdown_cues(resumed.id)
        self.alert_manager.notify_task_started(resumed.title, resumed.remaining_seconds)
        self._increment_metric("tasks_resumed")
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
        self._increment_metric("tasks_updated")
        return task

    def reset_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        reset = self.timer_engine.reset(task)
        self.repository.upsert(reset)
        self.alert_manager.clear_countdown_cues(reset.id)
        self._increment_metric("tasks_reset")
        return reset

    def complete_task(self, task_id: str, now: datetime | None = None) -> Task:
        task = self.get_task(task_id)
        task.status = TaskStatus.COMPLETED
        task.remaining_seconds = 0
        task.target_at = None
        task.finished_at = now
        self.repository.upsert(task)
        self.alert_manager.clear_countdown_cues(task.id)
        self.alert_manager.notify_task_finished(task.title)
        self._increment_metric("tasks_completed")
        self._start_next_subtask_if_any(task, now=now)
        return task

    def archive_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        if task.status == TaskStatus.RUNNING:
            raise ValueError("Pause the task before archiving")
        task.status = TaskStatus.ARCHIVED
        task.target_at = None
        self.repository.upsert(task)
        self.alert_manager.clear_countdown_cues(task.id)
        self._increment_metric("tasks_archived")
        return task

    def delete_task(self, task_id: str) -> None:
        self.repository.delete(task_id)
        self.alert_manager.clear_countdown_cues(task_id)
        self._increment_metric("tasks_deleted")

    def restore_task_snapshot(self, task: Task) -> Task:
        if task.status == TaskStatus.RUNNING:
            self._ensure_no_other_running(task.id)
        self.repository.upsert(task)
        self._increment_metric("tasks_restored")
        return task

    def snooze_task(self, task_id: str, minutes: int, now: datetime | None = None) -> Task:
        if minutes <= 0:
            raise ValueError("Snooze minutes must be > 0")
        task = self.get_task(task_id)
        self._ensure_no_other_running(task.id)
        task.remaining_seconds = minutes * 60
        task.status = TaskStatus.PAUSED
        task.finished_at = None
        task.target_at = None
        snoozed = self.timer_engine.resume(task, now=now)
        self.repository.upsert(snoozed)
        self.alert_manager.clear_countdown_cues(snoozed.id)
        self.alert_manager.notify_task_started(snoozed.title, snoozed.remaining_seconds)
        self._increment_metric("tasks_snoozed")
        return snoozed

    def tick(self, now: datetime | None = None) -> list[Task]:
        changed: list[Task] = []
        for task in self.repository.list_all():
            if task.status != TaskStatus.RUNNING:
                continue
            before_remaining = task.remaining_seconds
            before_status = task.status
            refreshed = self.timer_engine.refresh(task, now=now)
            self.alert_manager.maybe_play_countdown_cue(refreshed.id, refreshed.remaining_seconds)
            if refreshed.remaining_seconds != before_remaining or refreshed.status != before_status:
                self.repository.upsert(refreshed)
                changed.append(refreshed)
                if before_status == TaskStatus.RUNNING and refreshed.status == TaskStatus.EXPIRED:
                    self._increment_metric("tasks_expired")
                    self.alert_manager.clear_countdown_cues(refreshed.id)
                    self.alert_manager.alert_task_expired(
                        AlertEvent(task_id=refreshed.id, title=refreshed.title)
                    )
                    self.alert_manager.notify_task_finished(refreshed.title)
                    auto_started = self._start_next_subtask_if_any(refreshed, now=now)
                    if auto_started is not None:
                        changed.append(auto_started)
        return changed

    def recover_running_tasks(self, now: datetime | None = None) -> list[Task]:
        recovered: list[Task] = []
        for task in self.repository.list_all():
            if task.status != TaskStatus.RUNNING:
                continue
            refreshed = self.timer_engine.recover_running_task(task, now=now)
            self.repository.upsert(refreshed)
            recovered.append(refreshed)
            self._increment_metric("tasks_recovered")
        return recovered

    def set_strong_final_sound(self, enabled: bool) -> None:
        self.alert_manager.audio_backend.set_strong_final_sound(enabled)

    def set_notifications_enabled(self, enabled: bool) -> None:
        self.alert_manager.set_notifications_enabled(enabled)

    def _ensure_no_other_running(self, selected_task_id: str) -> None:
        for existing in self.repository.list_all():
            if existing.id != selected_task_id and existing.status == TaskStatus.RUNNING:
                raise ValueError("Only one running task is allowed at a time")

    def _next_sequence_order(self, parent_task_id: str) -> int:
        current = [
            task.sequence_order
            for task in self.repository.list_all()
            if task.parent_task_id == parent_task_id and task.sequence_order is not None
        ]
        if not current:
            return 0
        return max(current) + 1

    def _task_sequence_sort_key(self, task: Task) -> tuple[int, int, str]:
        if task.sequence_order is None:
            return (1, 0, task.created_at.isoformat())
        return (0, task.sequence_order, task.created_at.isoformat())

    def _increment_metric(self, metric_name: str) -> None:
        try:
            self.metrics.increment(metric_name)
        except Exception:
            return

    def _start_next_subtask_if_any(
        self,
        expired_task: Task,
        now: datetime | None = None,
    ) -> Task | None:
        if expired_task.parent_task_id is None:
            siblings = self.list_subtasks(expired_task.id)
            ordered_pending = [
                task
                for task in siblings
                if task.status in {TaskStatus.PENDING, TaskStatus.PAUSED}
            ]
            if not ordered_pending:
                return None
            next_task = ordered_pending[0]
            if next_task.status == TaskStatus.PAUSED:
                return self.resume_task(next_task.id, now=now)
            return self.start_task(next_task.id, now=now)

        siblings = self.list_subtasks(expired_task.parent_task_id)
        ordered_pending = [
            task
            for task in siblings
            if task.status in {TaskStatus.PENDING, TaskStatus.PAUSED}
        ]
        if not ordered_pending:
            return None

        next_task = next(
            (
                task
                for task in ordered_pending
                if (
                    expired_task.sequence_order is None
                    or task.sequence_order is None
                    or task.sequence_order > expired_task.sequence_order
                )
            ),
            ordered_pending[0],
        )

        if next_task.status == TaskStatus.PAUSED:
            return self.resume_task(next_task.id, now=now)
        return self.start_task(next_task.id, now=now)
