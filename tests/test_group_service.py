"""Unit tests for group task service."""

from __future__ import annotations

import pytest

from pulse_task.core.group import GroupStatus, TaskGroup
from pulse_task.core.group_service import GroupService
from pulse_task.core.persistence import Database


@pytest.fixture
def db() -> Database:
    """Create in-memory test database."""
    return Database(":memory:")


@pytest.fixture
def service(db: Database) -> GroupService:
    """Create GroupService with test database."""
    return GroupService(db)


@pytest.fixture
def sample_group(service: GroupService) -> TaskGroup:
    """Create sample group with 4 tasks."""
    return service.create_group(
        name="Dev workflow",
        task_ids=["review", "fix", "test", "push"],
        total_time_seconds=3600,
        description="Code review and deployment workflow",
    )


class TestGroupCreation:
    """Tests for group creation."""

    def test_create_group_success(self, service: GroupService) -> None:
        """Test successful group creation."""
        group = service.create_group(
            name="Test group",
            task_ids=["task1", "task2"],
            total_time_seconds=1800,
        )
        assert group.name == "Test group"
        assert group.status == GroupStatus.IDLE
        assert group.total_time_seconds == 1800
        assert group.tasks_completed == 0
        assert group.tasks_skipped == 0

    def test_create_group_empty_name_fails(self, service: GroupService) -> None:
        """Test that empty group name is rejected."""
        with pytest.raises(ValueError, match="name is required"):
            service.create_group(
                name="",
                task_ids=["task1"],
                total_time_seconds=1800,
            )

    def test_create_group_empty_tasks_fails(self, service: GroupService) -> None:
        """Test that empty task list is rejected."""
        with pytest.raises(ValueError, match="task_ids cannot be empty"):
            service.create_group(
                name="Test",
                task_ids=[],
                total_time_seconds=1800,
            )

    def test_create_group_invalid_time_fails(self, service: GroupService) -> None:
        """Test that non-positive time is rejected."""
        with pytest.raises(ValueError, match="total_time_seconds must be > 0"):
            service.create_group(
                name="Test",
                task_ids=["task1"],
                total_time_seconds=0,
            )

    def test_create_group_persisted(self, service: GroupService) -> None:
        """Test that created group is persisted."""
        group = service.create_group(
            name="Persistent group",
            task_ids=["a", "b"],
            total_time_seconds=900,
        )
        retrieved = service.get_group(group.id)
        assert retrieved is not None
        assert retrieved.name == "Persistent group"


class TestGroupRetrieval:
    """Tests for group retrieval."""

    def test_get_group_exists(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test retrieving existing group."""
        retrieved = service.get_group(sample_group.id)
        assert retrieved is not None
        assert retrieved.id == sample_group.id
        assert retrieved.name == sample_group.name

    def test_get_group_not_exists(self, service: GroupService) -> None:
        """Test retrieving non-existent group."""
        retrieved = service.get_group("nonexistent")
        assert retrieved is None

    def test_list_groups_empty(self, service: GroupService) -> None:
        """Test listing groups when none exist."""
        groups = service.list_groups()
        assert groups == []

    def test_list_groups_multiple(self, service: GroupService) -> None:
        """Test listing multiple groups."""
        g1 = service.create_group("Group 1", ["t1"], 900)
        g2 = service.create_group("Group 2", ["t2"], 1800)
        
        groups = service.list_groups()
        assert len(groups) == 2
        assert g1.id in [g.id for g in groups]
        assert g2.id in [g.id for g in groups]

    def test_list_groups_by_status(self, service: GroupService) -> None:
        """Test filtering groups by status."""
        g1 = service.create_group("Group 1", ["t1"], 900)
        g2 = service.create_group("Group 2", ["t2"], 1800)
        
        service.start_group_execution(g1.id)
        
        idle_groups = service.list_groups(status=GroupStatus.IDLE)
        assert len(idle_groups) == 1
        assert idle_groups[0].id == g2.id
        
        executing_groups = service.list_groups(status=GroupStatus.EXECUTING)
        assert len(executing_groups) == 1
        assert executing_groups[0].id == g1.id


class TestGroupExecution:
    """Tests for group execution lifecycle."""

    def test_start_group_execution(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test starting group execution."""
        group = service.start_group_execution(sample_group.id)
        assert group.status == GroupStatus.EXECUTING
        assert group.started_at is not None

    def test_start_group_not_idle_fails(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test that starting non-idle group fails."""
        service.start_group_execution(sample_group.id)
        with pytest.raises(ValueError, match="Cannot start group"):
            service.start_group_execution(sample_group.id)

    def test_pause_group_execution(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test pausing group execution."""
        service.start_group_execution(sample_group.id)
        group = service.pause_group_execution(sample_group.id)
        assert group.status == GroupStatus.PAUSED
        assert group.paused_at is not None

    def test_pause_non_executing_fails(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test that pausing non-executing group fails."""
        with pytest.raises(ValueError, match="Cannot pause group"):
            service.pause_group_execution(sample_group.id)

    def test_resume_group_execution(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test resuming paused group."""
        service.start_group_execution(sample_group.id)
        service.pause_group_execution(sample_group.id)
        group = service.resume_group_execution(sample_group.id)
        assert group.status == GroupStatus.EXECUTING
        assert group.paused_at is None

    def test_resume_non_paused_fails(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test that resuming non-paused group fails."""
        with pytest.raises(ValueError, match="Cannot resume group"):
            service.resume_group_execution(sample_group.id)


class TestTaskAdvancement:
    """Tests for task advancement within groups."""

    def test_advance_to_next_task(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test advancing to next task."""
        next_task = service.advance_to_next_task(sample_group.id)
        assert next_task == "fix"
        
        group = service.get_group(sample_group.id)
        assert group.tasks_completed == 1
        assert group.current_task_index == 1

    def test_advance_through_all_tasks(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test advancing through entire group."""
        for _i in range(4):
            service.advance_to_next_task(sample_group.id)
        
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.COMPLETED
        assert group.tasks_completed == 4
        assert group.current_task_id() is None

    def test_skip_task_in_group(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test skipping current task."""
        next_task = service.skip_task_in_group(sample_group.id)
        assert next_task == "fix"
        
        group = service.get_group(sample_group.id)
        assert group.tasks_skipped == 1
        assert group.current_task_index == 1

    def test_skip_advances_index(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test that skipping correctly advances current_task_index."""
        service.skip_task_in_group(sample_group.id)
        service.skip_task_in_group(sample_group.id)
        
        group = service.get_group(sample_group.id)
        assert group.tasks_skipped == 2
        assert group.current_task_id() == "test"


class TestGroupProgress:
    """Tests for group progress tracking."""

    def test_time_remaining_initially_full(self, sample_group: TaskGroup) -> None:
        """Test time remaining at start."""
        assert sample_group.time_remaining_seconds() == 3600

    def test_time_remaining_after_elapsed(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test time remaining after some elapsed time."""
        service.update_group_elapsed_time(sample_group.id, 600)
        group = service.get_group(sample_group.id)
        assert group.time_remaining_seconds() == 3000

    def test_time_remaining_zero_when_expired(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test time remaining is 0 when group expired."""
        service.update_group_elapsed_time(sample_group.id, 3600)
        group = service.get_group(sample_group.id)
        assert group.time_remaining_seconds() == 0

    def test_progress_percent_at_start(self, sample_group: TaskGroup) -> None:
        """Test progress percentage at start."""
        assert sample_group.progress_percent() == 0

    def test_progress_percent_midway(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test progress percentage midway through."""
        service.advance_to_next_task(sample_group.id)
        service.advance_to_next_task(sample_group.id)
        
        group = service.get_group(sample_group.id)
        assert group.progress_percent() == 50

    def test_progress_percent_complete(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test progress percentage when complete."""
        for _ in range(4):
            service.advance_to_next_task(sample_group.id)
        
        group = service.get_group(sample_group.id)
        assert group.progress_percent() == 100

    def test_progress_includes_skipped(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test that skipped tasks count toward progress."""
        service.skip_task_in_group(sample_group.id)
        service.advance_to_next_task(sample_group.id)
        
        group = service.get_group(sample_group.id)
        assert group.progress_percent() == 50


class TestGroupDeletion:
    """Tests for group deletion (archiving)."""

    def test_delete_group_archives(self, service: GroupService, sample_group: TaskGroup) -> None:
        """Test that deleting group archives it."""
        service.delete_group(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.ARCHIVED
        assert group.archived_at is not None

    def test_delete_nonexistent_fails(self, service: GroupService) -> None:
        """Test that deleting non-existent group fails."""
        with pytest.raises(ValueError, match="not found"):
            service.delete_group("nonexistent")


class TestGroupProperties:
    """Tests for TaskGroup properties."""

    def test_is_active(self, sample_group: TaskGroup) -> None:
        """Test is_active property."""
        assert not sample_group.is_active()
        sample_group.status = GroupStatus.EXECUTING
        assert sample_group.is_active()

    def test_is_complete(self, sample_group: TaskGroup) -> None:
        """Test is_complete property."""
        assert not sample_group.is_complete()
        sample_group.tasks_completed = 4
        assert sample_group.is_complete()

    def test_current_task_id_valid(self, sample_group: TaskGroup) -> None:
        """Test current_task_id when valid."""
        assert sample_group.current_task_id() == "review"

    def test_current_task_id_after_advance(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test current_task_id after advancement."""
        service.advance_to_next_task(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.current_task_id() == "fix"

    def test_has_next_task(self, sample_group: TaskGroup) -> None:
        """Test has_next_task property."""
        assert sample_group.has_next_task()
        sample_group.current_task_index = 4
        assert not sample_group.has_next_task()
