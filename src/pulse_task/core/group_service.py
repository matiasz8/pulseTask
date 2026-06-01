"""Group task service.

Manages CRUD operations and business logic for task groups.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol, cast

from pulse_task.core.group import GroupStatus, TaskGroup
from pulse_task.core.persistence import Database

logger = logging.getLogger(__name__)


class NotificationManagerProtocol(Protocol):
    """Notification API used by GroupService."""

    @property
    def warning_threshold_seconds(self) -> int:
        """Return warning threshold in seconds."""

    def send_task_expired(
        self,
        task_name: str,
        *,
        on_snooze: Callable[[], None] | None = None,
        on_start_next: Callable[[], None] | None = None,
    ) -> int | None:
        """Send a task expired notification."""

    def send_time_warning(
        self,
        task_name: str,
        seconds_remaining: int,
        *,
        on_extend: Callable[[], None] | None = None,
    ) -> int | None:
        """Send a time warning notification."""

    def send_focus_lost(
        self,
        task_name: str,
        *,
        on_resume: Callable[[], None] | None = None,
    ) -> int | None:
        """Send a focus lost notification."""


class GroupService:
    """Business logic for task group operations."""

    def __init__(
        self,
        db: Database,
        notification_manager: NotificationManagerProtocol | None = None,
    ) -> None:
        """Initialize GroupService with database connection.

        Args:
            db: Database instance for persistence
            notification_manager: Optional desktop notification manager
        """
        self.db = db
        self.notification_manager = notification_manager
        self._warning_notifications_sent: set[tuple[str, str]] = set()
        self._expired_notifications_sent: set[tuple[str, str]] = set()

    # CRUD Operations

    def create_group(
        self,
        name: str,
        task_ids: list[str],
        total_time_seconds: int = 3600,
        description: str = "",
    ) -> TaskGroup:
        """Create a new task group.

        Args:
            name: Group name
            task_ids: List of task IDs in execution order
            total_time_seconds: Total time budget for group
            description: Optional group description

        Returns:
            Created TaskGroup instance

        Raises:
            ValueError: If validation fails
        """
        group = TaskGroup(
            name=name,
            description=description,
            task_ids=task_ids,
            total_time_seconds=total_time_seconds,
        )
        self._insert_group(group)
        return group

    def get_group(self, group_id: str) -> TaskGroup | None:
        """Retrieve group by ID.

        Args:
            group_id: Group ID to retrieve

        Returns:
            TaskGroup if found, None otherwise
        """
        query = "SELECT * FROM task_groups WHERE id = ?"
        row = self.db.fetch_one(query, (group_id,))
        if not row:
            return None
        return self._row_to_group(row)

    def list_groups(
        self,
        status: GroupStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TaskGroup]:
        """List groups with optional filtering.

        Args:
            status: Filter by status (None = all)
            limit: Maximum results to return
            offset: Results offset for pagination

        Returns:
            List of TaskGroup instances
        """
        if status:
            query = (
                "SELECT * FROM task_groups WHERE status = ? "
                "ORDER BY created_at DESC LIMIT ? OFFSET ?"
            )
            rows = self.db.fetch_all(query, (status.value, limit, offset))
        else:
            query = "SELECT * FROM task_groups ORDER BY created_at DESC LIMIT ? OFFSET ?"
            rows = self.db.fetch_all(query, (limit, offset))

        return [self._row_to_group(row) for row in rows]

    def update_group(self, group: TaskGroup) -> None:
        """Update group in database.

        Args:
            group: TaskGroup to update
        """
        query = """
        UPDATE task_groups SET
            name = ?, description = ?, status = ?,
            task_ids = ?, total_time_seconds = ?,
            elapsed_time_seconds = ?, paused_time_seconds = ?,
            current_task_index = ?, tasks_completed = ?,
            tasks_skipped = ?, started_at = ?,
            completed_at = ?, archived_at = ?, paused_at = ?
        WHERE id = ?
        """
        self.db.execute(
            query,
            (
                group.name,
                group.description,
                group.status.value,
                json.dumps(group.task_ids),
                group.total_time_seconds,
                group.elapsed_time_seconds,
                group.paused_time_seconds,
                group.current_task_index,
                group.tasks_completed,
                group.tasks_skipped,
                group.started_at.isoformat() if group.started_at else None,
                group.completed_at.isoformat() if group.completed_at else None,
                group.archived_at.isoformat() if group.archived_at else None,
                group.paused_at.isoformat() if group.paused_at else None,
                group.id,
            ),
        )

    def delete_group(self, group_id: str) -> None:
        """Soft delete: archive group instead.

        Args:
            group_id: Group ID to delete
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")
        group.status = GroupStatus.ARCHIVED
        group.archived_at = datetime.now(UTC)
        self.update_group(group)

    # Execution Operations

    def start_group_execution(self, group_id: str) -> TaskGroup:
        """Start executing group.

        Args:
            group_id: Group to start

        Returns:
            Updated TaskGroup

        Raises:
            ValueError: If group not found or invalid state
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")
        if group.status != GroupStatus.IDLE:
            raise ValueError(f"Cannot start group in {group.status} state")

        group.status = GroupStatus.EXECUTING
        group.started_at = datetime.now(UTC)
        self._clear_notification_state(group_id)
        self.update_group(group)
        return group

    def pause_group_execution(self, group_id: str) -> TaskGroup:
        """Pause group execution.

        Args:
            group_id: Group to pause

        Returns:
            Updated TaskGroup

        Raises:
            ValueError: If group not found or not executing
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")
        if group.status != GroupStatus.EXECUTING:
            raise ValueError(f"Cannot pause group in {group.status} state")

        group.status = GroupStatus.PAUSED
        group.paused_at = datetime.now(UTC)
        self.update_group(group)
        return group

    def resume_group_execution(self, group_id: str) -> TaskGroup:
        """Resume paused group.

        Args:
            group_id: Group to resume

        Returns:
            Updated TaskGroup

        Raises:
            ValueError: If group not found or not paused
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")
        if group.status != GroupStatus.PAUSED:
            raise ValueError(f"Cannot resume group in {group.status} state")

        if group.paused_at:
            pause_duration = (datetime.now(UTC) - group.paused_at).total_seconds()
            group.paused_time_seconds += int(pause_duration)

        group.status = GroupStatus.EXECUTING
        group.paused_at = None
        self.update_group(group)
        return group

    def advance_to_next_task(self, group_id: str) -> str | None:
        """Advance to next task in group.

        Args:
            group_id: Group to advance

        Returns:
            ID of next task, or None if group is complete

        Raises:
            ValueError: If group not found
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        current_task_id = group.current_task_id()

        # Mark current task as completed if exists
        # (only if not already marked as skipped)
        total_processed = group.tasks_completed + group.tasks_skipped
        if current_task_id and total_processed < group.current_task_index + 1:
            group.tasks_completed += 1

        self._clear_notification_state(group_id, current_task_id)

        # Move to next task
        group.current_task_index += 1

        # Check if group is complete
        if group.is_complete():
            group.status = GroupStatus.COMPLETED
            group.completed_at = datetime.now(UTC)

        self.update_group(group)
        return group.current_task_id()

    def skip_task_in_group(self, group_id: str) -> str | None:
        """Skip current task and move to next.

        Args:
            group_id: Group whose current task to skip

        Returns:
            ID of next task after skipped task

        Raises:
            ValueError: If group not found
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        current_task_id = group.current_task_id()
        group.tasks_skipped += 1
        self._clear_notification_state(group_id, current_task_id)

        # Move to next task without incrementing tasks_completed
        group.current_task_index += 1

        # Check if group is complete
        if group.is_complete():
            group.status = GroupStatus.COMPLETED
            group.completed_at = datetime.now(UTC)

        self.update_group(group)
        return group.current_task_id()

    def update_group_elapsed_time(self, group_id: str, elapsed_seconds: int) -> TaskGroup:
        """Update elapsed time for group (called by timer).

        Args:
            group_id: Group to update
            elapsed_seconds: Total elapsed seconds

        Returns:
            Updated TaskGroup

        Raises:
            ValueError: If group not found
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        previous_remaining = group.time_remaining_seconds()
        current_task_id = group.current_task_id()

        group.elapsed_time_seconds = elapsed_seconds
        self.update_group(group)

        if current_task_id is not None:
            self._emit_time_notifications(group, current_task_id, previous_remaining)
        return group

    def extend_group_time(self, group_id: str, additional_seconds: int) -> TaskGroup:
        """Extend the current group's time budget."""
        if additional_seconds <= 0:
            raise ValueError("additional_seconds must be > 0")

        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Group {group_id} not found")

        group.total_time_seconds += additional_seconds
        self._clear_notification_state(group_id, group.current_task_id())
        self.update_group(group)
        return group

    def notify_focus_lost(self, group_id: str) -> None:
        """Emit a focus-lost notification for the current task."""
        if self.notification_manager is None:
            return

        group = self.get_group(group_id)
        if not group or group.status != GroupStatus.PAUSED:
            return

        task_name = group.current_task_id() or group.name
        self.notification_manager.send_focus_lost(
            task_name,
            on_resume=lambda: self._resume_if_current(group_id, task_name),
        )

    # Private Methods

    def _emit_time_notifications(
        self,
        group: TaskGroup,
        task_name: str,
        previous_remaining: int,
    ) -> None:
        """Send warning and expiration notifications when thresholds are crossed."""
        if self.notification_manager is None or group.status != GroupStatus.EXECUTING:
            return

        current_remaining = group.time_remaining_seconds()
        task_key = (group.id, task_name)
        threshold = max(1, self.notification_manager.warning_threshold_seconds)

        if (
            previous_remaining > threshold >= current_remaining > 0
            and task_key not in self._warning_notifications_sent
        ):
            self.notification_manager.send_time_warning(
                task_name,
                current_remaining,
                on_extend=lambda: self._extend_if_current(group.id, task_name, 300),
            )
            self._warning_notifications_sent.add(task_key)

        if (
            previous_remaining > 0
            and current_remaining == 0
            and task_key not in self._expired_notifications_sent
        ):
            self.notification_manager.send_task_expired(
                task_name,
                on_snooze=lambda: self._extend_if_current(group.id, task_name, 300),
                on_start_next=lambda: self._skip_if_current(group.id, task_name),
            )
            self._expired_notifications_sent.add(task_key)

    def _extend_if_current(self, group_id: str, task_name: str, additional_seconds: int) -> None:
        """Extend a group only if the same task is still active."""
        group = self.get_group(group_id)
        if group is None or group.current_task_id() != task_name:
            logger.info("Ignoring extend action for stale notification on %s", group_id)
            return
        self.extend_group_time(group_id, additional_seconds)

    def _skip_if_current(self, group_id: str, task_name: str) -> None:
        """Skip the current task only if the notification is still current."""
        group = self.get_group(group_id)
        if group is None or group.current_task_id() != task_name:
            logger.info("Ignoring skip action for stale notification on %s", group_id)
            return
        self.skip_task_in_group(group_id)

    def _resume_if_current(self, group_id: str, task_name: str | None) -> None:
        """Resume a paused group if the task has not changed."""
        group = self.get_group(group_id)
        if (
            group is None
            or group.current_task_id() != task_name
            or group.status != GroupStatus.PAUSED
        ):
            logger.info("Ignoring resume action for stale notification on %s", group_id)
            return
        self.resume_group_execution(group_id)

    def _clear_notification_state(self, group_id: str, task_name: str | None = None) -> None:
        """Forget notification state for a group or task."""
        keys = {
            key
            for key in self._warning_notifications_sent | self._expired_notifications_sent
            if key[0] == group_id and (task_name is None or key[1] == task_name)
        }
        self._warning_notifications_sent.difference_update(keys)
        self._expired_notifications_sent.difference_update(keys)

    def _insert_group(self, group: TaskGroup) -> None:
        """Insert new group into database."""
        query = """
        INSERT INTO task_groups (
            id, name, description, status, task_ids,
            total_time_seconds, elapsed_time_seconds,
            paused_time_seconds, current_task_index,
            tasks_completed, tasks_skipped, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(
            query,
            (
                group.id,
                group.name,
                group.description,
                group.status.value,
                json.dumps(group.task_ids),
                group.total_time_seconds,
                group.elapsed_time_seconds,
                group.paused_time_seconds,
                group.current_task_index,
                group.tasks_completed,
                group.tasks_skipped,
                group.created_at.isoformat(),
            ),
        )

    @staticmethod
    def _row_to_group(row: tuple[object, ...]) -> TaskGroup:
        """Convert database row to TaskGroup instance."""
        return TaskGroup(
            id=cast(str, row[0]),
            name=cast(str, row[1]),
            description=cast(str, row[2]),
            status=GroupStatus(cast(str, row[3])),
            task_ids=json.loads(cast(str, row[4])),
            total_time_seconds=cast(int, row[5]),
            elapsed_time_seconds=cast(int, row[6]),
            paused_time_seconds=cast(int, row[7]),
            current_task_index=cast(int, row[8]),
            tasks_completed=cast(int, row[9]),
            tasks_skipped=cast(int, row[10]),
            created_at=datetime.fromisoformat(cast(str, row[11])),
            started_at=(
                datetime.fromisoformat(cast(str, row[12]))
                if row[12] is not None
                else None
            ),
            completed_at=(
                datetime.fromisoformat(cast(str, row[13]))
                if row[13] is not None
                else None
            ),
            archived_at=(
                datetime.fromisoformat(cast(str, row[14]))
                if row[14] is not None
                else None
            ),
            paused_at=(
                datetime.fromisoformat(cast(str, row[15]))
                if row[15] is not None
                else None
            ),
        )
