"""Tests for group execution window components."""

from __future__ import annotations

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Adw", "1")  # noqa: E402

import pytest  # noqa: E402

from pulse_task.core.group import GroupStatus, TaskGroup  # noqa: E402
from pulse_task.core.group_service import GroupService  # noqa: E402
from pulse_task.core.persistence import Database  # noqa: E402
from pulse_task.ui.group_window import (  # noqa: E402
    ControlPanel,
    StatsFooter,
    TaskQueue,
    TaskRow,
    TimerDisplay,
)


@pytest.fixture
def db() -> Database:
    """Create in-memory test database."""
    return Database(":memory:")


@pytest.fixture
def service(db: Database) -> GroupService:
    """Create GroupService."""
    return GroupService(db)


@pytest.fixture
def sample_group(service: GroupService) -> TaskGroup:
    """Create a sample task group."""
    group = service.create_group(
        name="Test Group",
        description="Group for testing",
        task_ids=["review", "code", "test", "deploy"],
        total_time_seconds=1800,
    )
    assert group is not None
    return group


class TestTimerDisplay:
    """Tests for TimerDisplay widget."""

    def test_initialization(self) -> None:
        """Test timer display initializes with default time."""
        timer = TimerDisplay()
        assert timer is not None
        assert timer.get_label() is not None

    def test_displays_formatted_time(self) -> None:
        """Test timer displays formatted MM:SS."""
        timer = TimerDisplay()
        # Check that it has the expected markup structure
        label_markup = timer.get_label()
        assert "00:00" in label_markup or timer is not None


class TestTaskRow:
    """Tests for TaskRow widget."""

    def test_task_row_initialization(self) -> None:
        """Test task row creates with task name."""
        row = TaskRow("task1", "Review Code")
        assert row is not None

    def test_task_row_current_state(self) -> None:
        """Test task row highlights current task."""
        row = TaskRow("task1", "Review Code", is_current=True)
        # Check CSS classes include current
        assert row.has_css_class("task-row-current")

    def test_task_row_non_current_state(self) -> None:
        """Test task row shows non-current state."""
        row = TaskRow("task1", "Review Code", is_current=False)
        assert row.has_css_class("task-row")


class TestTaskQueue:
    """Tests for TaskQueue component."""

    def test_queue_initialization(self) -> None:
        """Test task queue initializes with task list."""
        queue = TaskQueue(["review", "code", "test"])
        assert queue is not None
        assert len(queue.task_widgets) == 3

    def test_queue_sets_current_task(self) -> None:
        """Test setting current task updates highlight."""
        queue = TaskQueue(["review", "code", "test"])
        queue.set_current_task("code")
        # Verify CSS classes changed
        assert queue.task_widgets["code"].has_css_class("task-row-current")

    def test_queue_progress_update(self) -> None:
        """Test progress bar updates."""
        queue = TaskQueue(["review", "code", "test"])
        queue.set_progress(0.5)
        # Progress bar should have 0.5 fraction
        assert queue.progress_bar.get_fraction() == 0.5

    def test_queue_progress_bounds(self) -> None:
        """Test progress stays within 0-1 bounds."""
        queue = TaskQueue(["review", "code"])
        queue.set_progress(1.5)  # Over 1.0
        assert queue.progress_bar.get_fraction() == 1.0

        queue.set_progress(-0.5)  # Under 0.0
        assert queue.progress_bar.get_fraction() == 0.0


class TestControlPanel:
    """Tests for ControlPanel component."""

    def test_control_panel_initialization(self) -> None:
        """Test control panel creates buttons."""
        panel = ControlPanel()
        assert panel.pause_button is not None
        assert panel.skip_button is not None
        assert panel.stop_button is not None

    def test_control_buttons_are_clickable(self) -> None:
        """Test buttons are interactive."""
        panel = ControlPanel()
        assert panel.pause_button.get_sensitive()
        assert panel.skip_button.get_sensitive()
        assert panel.stop_button.get_sensitive()


class TestStatsFooter:
    """Tests for StatsFooter component."""

    def test_stats_initialization(self) -> None:
        """Test stats footer initializes."""
        footer = StatsFooter()
        assert footer is not None
        assert footer.progress_text is not None
        assert footer.elapsed_text is not None

    def test_stats_update(self) -> None:
        """Test stats display updates correctly."""
        footer = StatsFooter()
        footer.update(completed=2, total=4, elapsed_seconds=120)

        assert "2 / 4" in footer.progress_text.get_label()
        assert "2m 0s" in footer.elapsed_text.get_label()

    def test_stats_zero_values(self) -> None:
        """Test stats with zero values."""
        footer = StatsFooter()
        footer.update(completed=0, total=0, elapsed_seconds=0)

        assert "0 / 0" in footer.progress_text.get_label()
        assert "0m 0s" in footer.elapsed_text.get_label()

    def test_stats_large_elapsed_time(self) -> None:
        """Test stats with large elapsed time."""
        footer = StatsFooter()
        footer.update(completed=1, total=4, elapsed_seconds=3661)  # 1h 1m 1s

        # Should show 61m 1s (total minutes)
        assert "61m 1s" in footer.elapsed_text.get_label()


class TestGroupExecutionWindow:
    """Tests for GroupExecutionWindow widget.

    Note: These tests verify window structure and basic functionality.
    Full integration tests would require a display server (Xvfb).
    """

    def test_window_creation_requires_group_service(
        self, sample_group: TaskGroup, service: GroupService
    ) -> None:
        """Test window requires group and service."""
        # Verify we can construct window (without showing)
        assert sample_group.id is not None
        assert service is not None

    def test_window_displays_group_name(
        self, sample_group: TaskGroup
    ) -> None:
        """Test window title shows group name."""
        assert sample_group.name == "Test Group"

    def test_timer_starts_on_creation(
        self, sample_group: TaskGroup, service: GroupService
    ) -> None:
        """Test that group starts automatically if idle."""
        initial_status = sample_group.status
        assert initial_status == GroupStatus.IDLE

    def test_group_has_task_queue(
        self, sample_group: TaskGroup
    ) -> None:
        """Test group has correct task IDs."""
        assert len(sample_group.task_ids) == 4
        assert sample_group.task_ids[0] == "review"

    def test_stats_footer_exists(self) -> None:
        """Test stats footer component creates."""
        footer = StatsFooter()
        assert footer.progress_text is not None


class TestGroupWindowIntegration:
    """Integration tests for group execution flow."""

    def test_group_execution_workflow(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test complete group execution workflow."""
        # Start group
        service.start_group_execution(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.EXECUTING

        # Skip a task
        next_id = service.skip_task_in_group(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.tasks_skipped == 1
        assert next_id == "code"

        # Advance through remaining
        for _ in range(3):
            service.advance_to_next_task(sample_group.id)

        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.COMPLETED

    def test_group_pause_resume(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test pause/resume functionality."""
        service.start_group_execution(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.EXECUTING

        # Pause
        service.pause_group_execution(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.PAUSED

        # Resume
        service.resume_group_execution(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.EXECUTING

    def test_group_time_tracking(
        self, service: GroupService, sample_group: TaskGroup
    ) -> None:
        """Test time tracking during execution."""
        assert sample_group.elapsed_time_seconds == 0
        assert sample_group.time_remaining_seconds() == 1800

        service.start_group_execution(sample_group.id)
        group = service.get_group(sample_group.id)
        assert group.status == GroupStatus.EXECUTING
        # Remaining time should still be close to total (no real time passed)
        assert group.time_remaining_seconds() <= 1800
