from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from pulse_task.system.audio import AudioBackend
from pulse_task.system.notify import NotificationBackend


@dataclass(slots=True)
class AlertEvent:
    task_id: str
    title: str


class AlertManager:
    """Coordinates expiration alerts with light debouncing."""

    def __init__(
        self,
        audio_backend: AudioBackend | None = None,
        notification_backend: NotificationBackend | None = None,
        debounce_seconds: float = 3.0,
        notifications_enabled: bool = True,
    ) -> None:
        self.audio_backend = audio_backend or AudioBackend()
        self.notification_backend = notification_backend or NotificationBackend()
        self.debounce_seconds = debounce_seconds
        self.notifications_enabled = notifications_enabled
        self._last_alert_at = 0.0
        self._countdown_cues: dict[str, int] = {}

    def set_notifications_enabled(self, enabled: bool) -> None:
        self.notifications_enabled = enabled

    def alert_task_expired(self, event: AlertEvent) -> bool:
        now = monotonic()
        if now - self._last_alert_at < self.debounce_seconds:
            return False

        self.audio_backend.play_alert()
        if self.notifications_enabled:
            self.notification_backend.send(
                title="Task expired",
                body=f"{event.title} has reached its deadline.",
            )
        self._last_alert_at = now
        return True

    def notify_task_started(self, title: str, remaining_seconds: int) -> None:
        minutes = max(1, remaining_seconds // 60)
        if minutes >= 60:
            hours = minutes // 60
            rem = minutes % 60
            if rem == 0:
                remaining = f"{hours}h"
            else:
                remaining = f"{hours}h and {rem} min"
        else:
            remaining = f"{minutes} min"
        if self.notifications_enabled:
            self.notification_backend.send(
                title="Task started",
                body=f"{title} - {remaining} remaining.",
            )

    def notify_task_finished(self, title: str) -> None:
        if self.notifications_enabled:
            self.notification_backend.send(
                title="Task finished",
                body=f"{title} finished. Starting next task if available.",
            )

    def maybe_play_countdown_cue(self, task_id: str, remaining_seconds: int) -> bool:
        if remaining_seconds < 1 or remaining_seconds > 3:
            return False
        if self._countdown_cues.get(task_id) == remaining_seconds:
            return False

        self.audio_backend.play_countdown_cue()
        self._countdown_cues[task_id] = remaining_seconds
        return True

    def clear_countdown_cues(self, task_id: str) -> None:
        self._countdown_cues.pop(task_id, None)
