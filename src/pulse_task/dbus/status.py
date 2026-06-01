"""Lightweight status interface for GNOME integrations."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pulse_task.core.group import GroupStatus, TaskGroup
from pulse_task.core.group_service import GroupService

logger = logging.getLogger(__name__)

SignalCallback = Callable[["StatusSnapshot"], None]


@dataclass(frozen=True, slots=True)
class StatusSnapshot:
    """Current execution snapshot exposed to GNOME integrations."""

    group_id: str | None = None
    group_name: str = ""
    current_task: str = ""
    is_paused: bool = False
    time_remaining: int = 0
    status: str = "Idle"

    @property
    def is_active(self) -> bool:
        """Return whether an active group is currently available."""
        return self.group_id is not None and self.status != "Idle"


class StatusInterface:
    """Expose active group state through D-Bus-like signals."""

    _GROUP_SIGNAL = "GroupStatusChanged"
    _TIME_SIGNAL = "TimeUpdated"
    _TASK_SIGNAL = "TaskChanged"

    def __init__(self, service: GroupService, settings: Any | None = None) -> None:
        """Initialize the interface.

        Args:
            service: Group service used as the canonical source of truth.
            settings: Optional Gio.Settings-compatible object.
        """
        self.service = service
        self.settings = settings
        self.current_group_id: str | None = None
        self._snapshot = StatusSnapshot()
        self._listeners: dict[str, dict[int, SignalCallback]] = {
            self._GROUP_SIGNAL: {},
            self._TIME_SIGNAL: {},
            self._TASK_SIGNAL: {},
        }
        self._next_handler_id = 1
        self._last_time_signal: int | None = None

    def connect(self, signal_name: str, callback: SignalCallback) -> int:
        """Register a listener for a status signal."""
        if signal_name not in self._listeners:
            raise ValueError(f"Unsupported signal: {signal_name}")

        handler_id = self._next_handler_id
        self._next_handler_id += 1
        self._listeners[signal_name][handler_id] = callback
        return handler_id

    def disconnect(self, handler_id: int) -> None:
        """Remove a previously registered signal listener."""
        for listeners in self._listeners.values():
            if handler_id in listeners:
                listeners.pop(handler_id, None)
                return

    def get_snapshot(self) -> StatusSnapshot:
        """Return the most recent status snapshot."""
        return self.refresh()

    def set_active_group(self, group_id: str | None) -> StatusSnapshot:
        """Track the group currently exposed to system integrations."""
        next_group_id = group_id or None
        changed = next_group_id != self.current_group_id
        self.current_group_id = next_group_id
        if self.settings is not None and hasattr(self.settings, "set_string"):
            try:
                self.settings.set_string("last-group-id", group_id or "")
            except Exception:  # pragma: no cover - defensive fallback
                logger.debug("Unable to persist last-group-id", exc_info=True)
        return self.refresh(force=changed)

    def clear_active_group(self) -> StatusSnapshot:
        """Clear the active group and emit an idle snapshot."""
        return self.set_active_group(None)

    def refresh(self, *, force: bool = False) -> StatusSnapshot:
        """Refresh the snapshot from GroupService and emit changed signals."""
        previous = self._snapshot
        snapshot = self._build_snapshot(self._resolve_group())
        self._snapshot = snapshot

        if force or (
            snapshot.group_id != previous.group_id
            or snapshot.group_name != previous.group_name
            or snapshot.is_paused != previous.is_paused
            or snapshot.status != previous.status
        ):
            self._emit(self._GROUP_SIGNAL, snapshot)

        if force or snapshot.current_task != previous.current_task:
            self._emit(self._TASK_SIGNAL, snapshot)

        if force or snapshot.time_remaining != previous.time_remaining:
            if force or snapshot.time_remaining != self._last_time_signal:
                self._last_time_signal = snapshot.time_remaining
                self._emit(self._TIME_SIGNAL, snapshot)

        return snapshot

    def set_paused(self, paused: bool) -> StatusSnapshot:
        """Pause or resume the tracked group via GroupService."""
        snapshot = self.get_snapshot()
        if snapshot.group_id is None:
            return snapshot

        try:
            if paused and not snapshot.is_paused:
                self.service.pause_group_execution(snapshot.group_id)
            elif not paused and snapshot.is_paused:
                self.service.resume_group_execution(snapshot.group_id)
        except ValueError:
            logger.debug("Unable to change pause state", exc_info=True)
        return self.refresh(force=True)

    def toggle_paused(self) -> StatusSnapshot:
        """Toggle the paused state for the active group."""
        snapshot = self.get_snapshot()
        if snapshot.group_id is None:
            return snapshot
        return self.set_paused(not snapshot.is_paused)

    def _resolve_group(self) -> TaskGroup | None:
        if self.current_group_id is None:
            return None
        return self.service.get_group(self.current_group_id)

    def _build_snapshot(self, group: TaskGroup | None) -> StatusSnapshot:
        if group is None or group.status in {GroupStatus.COMPLETED, GroupStatus.ARCHIVED}:
            return StatusSnapshot()

        status = {
            GroupStatus.EXECUTING: "Running",
            GroupStatus.PAUSED: "Paused",
            GroupStatus.IDLE: "Idle",
        }.get(group.status, "Idle")
        return StatusSnapshot(
            group_id=group.id,
            group_name=group.name,
            current_task=group.current_task_id() or "",
            is_paused=group.status == GroupStatus.PAUSED,
            time_remaining=max(0, group.time_remaining_seconds()),
            status=status,
        )

    def _emit(self, signal_name: str, snapshot: StatusSnapshot) -> None:
        for callback in tuple(self._listeners[signal_name].values()):
            callback(snapshot)
