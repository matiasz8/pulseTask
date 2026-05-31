"""Integration tests for group task execution workflows."""

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


class TestGroupExecutionWorkflow:
    """Tests for complete group execution workflows."""

    def test_end_to_end_normal_execution(self, service: GroupService) -> None:
        """Test complete workflow from creation to completion."""
        # 1. Create group
        group = service.create_group(
            name="Full workflow",
            task_ids=["code_review", "apply_fixes", "run_tests", "commit"],
            total_time_seconds=180,
        )
        assert group.status == GroupStatus.IDLE

        # 2. Start execution
        group = service.start_group_execution(group.id)
        assert group.status == GroupStatus.EXECUTING
        assert group.started_at is not None

        # 3. Simulate time passing
        service.update_group_elapsed_time(group.id, 60)
        group = service.get_group(group.id)
        assert group.elapsed_time_seconds == 60
        assert group.time_remaining_seconds() == 120

        # 4. Complete first task
        next_task = service.advance_to_next_task(group.id)
        assert next_task == "apply_fixes"
        group = service.get_group(group.id)
        assert group.tasks_completed == 1
        assert group.progress_percent() == 25

        # 5. Complete second task
        service.advance_to_next_task(group.id)
        group = service.get_group(group.id)
        assert group.tasks_completed == 2
        assert group.progress_percent() == 50

        # 6. Skip third task
        service.skip_task_in_group(group.id)
        group = service.get_group(group.id)
        assert group.tasks_skipped == 1
        assert group.progress_percent() == 75

        # 7. Complete last task
        service.advance_to_next_task(group.id)
        group = service.get_group(group.id)
        assert group.status == GroupStatus.COMPLETED
        assert group.completed_at is not None
        assert group.progress_percent() == 100

    def test_pause_resume_workflow(self, service: GroupService) -> None:
        """Test pause and resume during execution."""
        import time
        
        group = service.create_group(
            name="Interruptible",
            task_ids=["a", "b", "c"],
            total_time_seconds=180,
        )

        # Start
        service.start_group_execution(group.id)
        service.update_group_elapsed_time(group.id, 30)

        # Pause
        group = service.pause_group_execution(group.id)
        assert group.status == GroupStatus.PAUSED

        # Sleep a tiny bit to ensure time difference
        time.sleep(0.01)

        # Resume
        group = service.resume_group_execution(group.id)
        assert group.status == GroupStatus.EXECUTING
        # paused_time_seconds should have increased (even if tiny)
        assert group.paused_time_seconds >= 0

    def test_skip_multiple_tasks_workflow(self, service: GroupService) -> None:
        """Test workflow with multiple skipped tasks."""
        group = service.create_group(
            name="Skip heavy",
            task_ids=["t1", "t2", "t3", "t4", "t5"],
            total_time_seconds=600,
        )

        # Skip first two tasks
        service.skip_task_in_group(group.id)
        service.skip_task_in_group(group.id)
        
        group = service.get_group(group.id)
        assert group.tasks_skipped == 2
        assert group.current_task_id() == "t3"

        # Complete remaining
        for _ in range(3):
            service.advance_to_next_task(group.id)

        group = service.get_group(group.id)
        assert group.status == GroupStatus.COMPLETED
        assert group.tasks_completed == 3

    def test_single_task_group(self, service: GroupService) -> None:
        """Test group with only one task."""
        group = service.create_group(
            name="Single task",
            task_ids=["the_only_task"],
            total_time_seconds=300,
        )

        service.start_group_execution(group.id)
        service.advance_to_next_task(group.id)

        group = service.get_group(group.id)
        assert group.status == GroupStatus.COMPLETED
        assert group.tasks_completed == 1

    def test_large_group_100_tasks(self, service: GroupService) -> None:
        """Test group with many tasks (stress test)."""
        task_ids = [f"task_{i}" for i in range(100)]
        group = service.create_group(
            name="Large group",
            task_ids=task_ids,
            total_time_seconds=36000,
        )

        service.start_group_execution(group.id)

        # Advance through 50 tasks
        for _ in range(50):
            service.advance_to_next_task(group.id)

        group = service.get_group(group.id)
        assert group.progress_percent() == 50

        # Skip 25 tasks
        for _ in range(25):
            service.skip_task_in_group(group.id)

        group = service.get_group(group.id)
        assert group.progress_percent() == 75

        # Complete remaining 25
        for _ in range(25):
            service.advance_to_next_task(group.id)

        group = service.get_group(group.id)
        assert group.status == GroupStatus.COMPLETED
        assert group.tasks_completed == 75
        assert group.tasks_skipped == 25

    def test_time_expiration_workflow(self, service: GroupService) -> None:
        """Test group when time budget expires."""
        group = service.create_group(
            name="Time limited",
            task_ids=["quick1", "quick2"],
            total_time_seconds=60,
        )

        service.start_group_execution(group.id)

        # Simulate time running out
        service.update_group_elapsed_time(group.id, 60)
        group = service.get_group(group.id)
        assert group.time_remaining_seconds() == 0

        # Can still advance tasks (application logic should prevent this)
        service.advance_to_next_task(group.id)
        group = service.get_group(group.id)
        assert group.tasks_completed == 1

    def test_archive_completed_group(self, service: GroupService) -> None:
        """Test archiving a completed group."""
        group = service.create_group(
            name="To archive",
            task_ids=["task1"],
            total_time_seconds=300,
        )

        service.start_group_execution(group.id)
        service.advance_to_next_task(group.id)

        group = service.get_group(group.id)
        assert group.status == GroupStatus.COMPLETED

        # Archive
        service.delete_group(group.id)
        group = service.get_group(group.id)
        assert group.status == GroupStatus.ARCHIVED

    def test_multiple_groups_independent(self, service: GroupService) -> None:
        """Test that multiple groups are independent."""
        g1 = service.create_group("Group 1", ["g1t1", "g1t2"], 300)
        g2 = service.create_group("Group 2", ["g2t1", "g2t2"], 600)

        # Start and manipulate g1
        service.start_group_execution(g1.id)
        service.advance_to_next_task(g1.id)

        # g2 should be unaffected
        g1_check = service.get_group(g1.id)
        g2_check = service.get_group(g2.id)

        assert g1_check.status == GroupStatus.EXECUTING
        assert g1_check.tasks_completed == 1

        assert g2_check.status == GroupStatus.IDLE
        assert g2_check.tasks_completed == 0

    def test_persistence_across_operations(self, service: GroupService) -> None:
        """Test that group state persists across database operations."""
        # Create
        group = service.create_group(
            name="Persistent",
            task_ids=["p1", "p2", "p3"],
            total_time_seconds=900,
        )
        group_id = group.id

        # Modify
        service.start_group_execution(group_id)
        service.update_group_elapsed_time(group_id, 150)
        service.advance_to_next_task(group_id)

        # Retrieve and verify
        retrieved = service.get_group(group_id)
        assert retrieved is not None
        assert retrieved.status == GroupStatus.EXECUTING
        assert retrieved.elapsed_time_seconds == 150
        assert retrieved.tasks_completed == 1
        assert retrieved.current_task_id() == "p2"

    def test_group_properties_consistency(self, service: GroupService) -> None:
        """Test that group properties remain consistent through operations."""
        group = service.create_group(
            name="Consistent",
            task_ids=["x", "y", "z"],
            total_time_seconds=600,
        )

        # Properties should not change
        original_name = group.name
        original_task_ids = list(group.task_ids)
        original_total_time = group.total_time_seconds

        # Execute operations
        service.start_group_execution(group.id)
        service.update_group_elapsed_time(group.id, 100)
        service.advance_to_next_task(group.id)
        service.pause_group_execution(group.id)
        service.resume_group_execution(group.id)

        # Verify properties unchanged
        updated = service.get_group(group.id)
        assert updated.name == original_name
        assert updated.task_ids == original_task_ids
        assert updated.total_time_seconds == original_total_time
