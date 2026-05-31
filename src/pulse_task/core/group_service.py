"""Group task service.

Manages CRUD operations and business logic for task groups.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from pulse_task.core.group import GroupMember, GroupStatus, TaskGroup
from pulse_task.core.persistence import Database


class GroupService:
    """Business logic for task group operations."""

    def __init__(self, db: Database) -> None:
        """Initialize GroupService with database connection.

        Args:
            db: Database instance for persistence
        """
        self.db = db

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
            query = "SELECT * FROM task_groups WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
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

        # Mark current task as completed if exists (only if not already marked as skipped)
        if group.current_task_id() and group.tasks_completed + group.tasks_skipped < group.current_task_index + 1:
            group.tasks_completed += 1

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

        group.tasks_skipped += 1
        
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

        group.elapsed_time_seconds = elapsed_seconds
        self.update_group(group)
        return group

    # Private Methods

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
    def _row_to_group(row: tuple) -> TaskGroup:
        """Convert database row to TaskGroup instance."""
        return TaskGroup(
            id=row[0],
            name=row[1],
            description=row[2],
            status=GroupStatus(row[3]),
            task_ids=json.loads(row[4]),
            total_time_seconds=row[5],
            elapsed_time_seconds=row[6],
            paused_time_seconds=row[7],
            current_task_index=row[8],
            tasks_completed=row[9],
            tasks_skipped=row[10],
            created_at=datetime.fromisoformat(row[11]),
            started_at=datetime.fromisoformat(row[12]) if row[12] else None,
            completed_at=datetime.fromisoformat(row[13]) if row[13] else None,
            archived_at=datetime.fromisoformat(row[14]) if row[14] else None,
            paused_at=datetime.fromisoformat(row[15]) if row[15] else None,
        )
