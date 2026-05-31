"""Tests for D-Bus service integration (FASE 3.1 Stubs).

Note: D-Bus service is stubbed for v0.3.0. These tests verify the
wrapper interface and GroupService method binding, not D-Bus itself.
"""

import pytest

from pulse_task.core.group_service import GroupService
from pulse_task.core.persistence import Database
from pulse_task.dbus.service import DBusService


@pytest.fixture
def db():
    """Create in-memory test database."""
    return Database(":memory:")


@pytest.fixture
def service(db):
    """Create test GroupService."""
    return GroupService(db)


@pytest.fixture
def dbus_service(service):
    """Create test DBusService."""
    return DBusService(service)


@pytest.fixture
def group_with_tasks(service):
    """Create test group with tasks."""
    return service.create_group(
        name="Test Group",
        task_ids=["task_1", "task_2", "task_3"],
        total_time_seconds=600
    )


class TestDBusServiceStatus:
    """Test D-Bus status properties."""

    def test_get_status_idle_when_no_active_group(self, dbus_service):
        """Status should be IDLE when no group active."""
        assert dbus_service.get_status() == "IDLE"

    def test_get_status_idle_when_group_not_started(self, dbus_service, group_with_tasks):
        """Status should be idle when group created but not started."""
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_status() == "idle"

    def test_get_status_executing_when_group_started(self, service, dbus_service, group_with_tasks):
        """Status should be executing when group started."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_status() == "executing"

    def test_get_is_executing_true_when_status_executing(
        self, service, dbus_service, group_with_tasks
    ):
        """IsExecuting should be true when status is executing."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_is_executing() is True

    def test_get_is_executing_false_when_status_idle(self, dbus_service):
        """IsExecuting should be false when status is IDLE."""
        assert dbus_service.get_is_executing() is False


class TestDBusServiceTasks:
    """Test D-Bus task-related properties."""

    def test_get_current_task_name_empty_when_no_active_group(self, dbus_service):
        """Current task name should be empty when no active group."""
        assert dbus_service.get_current_task_name() == ""

    def test_get_current_task_name_returns_first_task(self, service, dbus_service, group_with_tasks):
        """Current task name should be first task after starting."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_current_task_name() == "task_1"

    def test_get_current_task_name_changes_on_advance(self, service, dbus_service, group_with_tasks):
        """Current task name should change after advancing."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_current_task_name() == "task_1"

        service.advance_to_next_task(group_with_tasks.id)
        assert dbus_service.get_current_task_name() == "task_2"

    def test_get_time_remaining_zero_when_no_active_group(self, dbus_service):
        """Time remaining should be 0 when no active group."""
        assert dbus_service.get_time_remaining() == 0

    def test_get_time_remaining_returns_positive_value(self, service, dbus_service, group_with_tasks):
        """Time remaining should be positive for active group."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        remaining = dbus_service.get_time_remaining()
        assert remaining > 0
        assert remaining <= 600


class TestDBusServiceMethods:
    """Test D-Bus method calls."""

    def test_set_paused_true_pauses_group(self, service, dbus_service, group_with_tasks):
        """SetPaused(true) should pause group execution."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_status() == "executing"

        dbus_service.set_paused(True)
        assert dbus_service.get_status() == "paused"

    def test_set_paused_false_resumes_group(self, service, dbus_service, group_with_tasks):
        """SetPaused(false) should resume group execution."""
        service.start_group_execution(group_with_tasks.id)
        service.pause_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_status() == "paused"

        dbus_service.set_paused(False)
        assert dbus_service.get_status() == "executing"

    def test_skip_current_task_advances_to_next(self, service, dbus_service, group_with_tasks):
        """SkipCurrentTask should advance to next task."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id
        assert dbus_service.get_current_task_name() == "task_1"

        dbus_service.skip_current_task()
        assert dbus_service.get_current_task_name() == "task_2"

    def test_skip_current_task_counts_as_interruption(self, service, dbus_service, group_with_tasks):
        """SkipCurrentTask should count as interruption in stats."""
        service.start_group_execution(group_with_tasks.id)
        dbus_service.current_group_id = group_with_tasks.id

        group_before = service.get_group(group_with_tasks.id)
        skipped_before = group_before.tasks_skipped

        dbus_service.skip_current_task()

        group_after = service.get_group(group_with_tasks.id)
        assert group_after.tasks_skipped == skipped_before + 1

    def test_set_paused_ignored_when_no_active_group(self, dbus_service):
        """SetPaused should be ignored when no active group."""
        dbus_service.set_paused(True)  # Should not raise
        assert dbus_service.get_status() == "IDLE"

    def test_skip_ignored_when_no_active_group(self, dbus_service):
        """SkipCurrentTask should be ignored when no active group."""
        dbus_service.skip_current_task()  # Should not raise
        assert dbus_service.get_status() == "IDLE"

    def test_stop_ignored_when_no_active_group(self, dbus_service):
        """StopExecution should be ignored when no active group."""
        dbus_service.stop_execution()  # Should not raise
        assert dbus_service.get_status() == "IDLE"


class TestDBusServiceRegistration:
    """Test D-Bus service registration (v0.3.0 stubs)."""

    def test_register_returns_false_in_stub(self, dbus_service):
        """Register should return False (D-Bus stubbed for v0.3.0)."""
        result = dbus_service.register()
        assert result is False

    def test_unregister_clears_registration(self, dbus_service):
        """Unregister should clear registration flag."""
        dbus_service.unregister()
        assert dbus_service._is_registered is False


class TestDBusServiceSignals:
    """Test D-Bus signal emission (v0.3.0 stubs)."""

    def test_emit_status_changed_no_error(self, dbus_service):
        """EmitStatusChanged should not raise (signal is stubbed)."""
        dbus_service._is_registered = False
        dbus_service.emit_status_changed("executing")  # Should not raise

    def test_emit_time_updated_no_error(self, dbus_service):
        """EmitTimeUpdated should not raise (signal is stubbed)."""
        dbus_service._is_registered = False
        dbus_service.emit_time_updated(300)  # Should not raise

    def test_emit_task_changed_no_error(self, dbus_service):
        """EmitTaskChanged should not raise (signal is stubbed)."""
        dbus_service._is_registered = False
        dbus_service.emit_task_changed("task_1")  # Should not raise
