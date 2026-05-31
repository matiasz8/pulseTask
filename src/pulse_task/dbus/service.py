"""D-Bus service implementation for PulseTask GNOME integration.

Provides org.gnome.Pulse D-Bus service for:
- Quick Settings control (pause/resume)
- Shell notifications with action buttons
- Global keyboard shortcuts
- Search provider integration
"""

import logging

from pulse_task.core.group_service import GroupService

logger = logging.getLogger(__name__)


class DBusService:
    """D-Bus service for PulseTask GNOME integration.

    Exposes GroupService functionality over D-Bus for:
    - org.gnome.Pulse.Service interface
    - Quick Settings integration
    - System notifications
    - Global shortcuts
    """

    def __init__(self, service: GroupService) -> None:
        """Initialize D-Bus service.

        Args:
            service: GroupService instance to expose
        """
        self.service = service
        self.current_group_id: str | None = None
        self._session_bus = None
        self._is_registered = False

    def register(self) -> bool:
        """Register D-Bus service.

        Attempts to register org.gnome.Pulse on session bus.
        Gracefully fails if D-Bus unavailable (offline mode).

        Returns:
            True if registered successfully, False if D-Bus unavailable
        """
        try:
            # D-Bus registration would happen here
            # For now, stub implementation
            logger.info("D-Bus service registration: STUBBED (v0.3.0)")
            self._is_registered = False
            return False
        except Exception as e:
            logger.warning(f"D-Bus registration failed: {e}. Running offline.")
            return False

    def unregister(self) -> None:
        """Unregister D-Bus service."""
        self._is_registered = False
        logger.info("D-Bus service unregistered")

    # D-Bus methods (org.gnome.Pulse.Service)

    def get_status(self) -> str:
        """Get current group execution status.

        Returns:
            "IDLE", "EXECUTING", "PAUSED", or "COMPLETED"
        """
        if not self.current_group_id:
            return "IDLE"

        group = self.service.get_group(self.current_group_id)
        if not group:
            return "IDLE"

        return group.status.value

    def get_is_executing(self) -> bool:
        """Check if group is currently executing.

        Returns:
            True if group status is executing
        """
        return self.get_status() == "executing"

    def get_current_task_name(self) -> str:
        """Get name of current task in active group.

        Returns:
            Task name (task_id) or empty string if no active group
        """
        if not self.current_group_id:
            return ""

        group = self.service.get_group(self.current_group_id)
        if not group:
            return ""

        task_id = group.current_task_id()
        if not task_id:
            return ""

        return task_id

    def get_time_remaining(self) -> int:
        """Get seconds remaining for current task.

        Returns:
            Seconds remaining, 0 if no active group
        """
        if not self.current_group_id:
            return 0

        group = self.service.get_group(self.current_group_id)
        if not group:
            return 0

        return max(0, group.time_remaining_seconds())

    def set_paused(self, paused: bool) -> None:
        """Pause or resume group execution.

        Args:
            paused: True to pause, False to resume
        """
        if not self.current_group_id:
            return

        try:
            if paused:
                self.service.pause_group_execution(self.current_group_id)
                logger.info(f"D-Bus: Paused group {self.current_group_id}")
            else:
                self.service.resume_group_execution(self.current_group_id)
                logger.info(f"D-Bus: Resumed group {self.current_group_id}")
        except Exception as e:
            logger.error(f"D-Bus pause/resume failed: {e}")

    def skip_current_task(self) -> None:
        """Skip current task and advance to next."""
        if not self.current_group_id:
            return

        try:
            self.service.skip_task_in_group(self.current_group_id)
            logger.info(f"D-Bus: Skipped task in {self.current_group_id}")
        except Exception as e:
            logger.error(f"D-Bus skip failed: {e}")

    def stop_execution(self) -> None:
        """Stop group execution by advancing all remaining tasks."""
        if not self.current_group_id:
            return

        try:
            # Advance through all remaining tasks to mark complete
            while self.service.advance_to_next_task(self.current_group_id):
                pass
            logger.info(f"D-Bus: Stopped group {self.current_group_id}")
        except Exception as e:
            logger.error(f"D-Bus stop failed: {e}")

    # D-Bus signals (would be emitted in v0.3.0)

    def emit_status_changed(self, status: str) -> None:
        """Emit status-changed signal.

        Connected to:
        - Quick Settings toggle update
        - Shell integration refresh
        """
        if not self._is_registered:
            return
        logger.debug(f"Signal: status-changed({status})")

    def emit_time_updated(self, seconds_remaining: int) -> None:
        """Emit time-updated signal.

        Connected to:
        - Quick Settings time display
        - Notification center
        """
        if not self._is_registered:
            return
        logger.debug(f"Signal: time-updated({seconds_remaining})")

    def emit_task_changed(self, task_name: str) -> None:
        """Emit task-changed signal.

        Connected to:
        - Shell integration display
        - Notification updates
        """
        if not self._is_registered:
            return
        logger.debug(f"Signal: task-changed({task_name})")
