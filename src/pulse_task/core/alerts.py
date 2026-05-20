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
    ) -> None:
        self.audio_backend = audio_backend or AudioBackend()
        self.notification_backend = notification_backend or NotificationBackend()
        self.debounce_seconds = debounce_seconds
        self._last_alert_at = 0.0

    def alert_task_expired(self, event: AlertEvent) -> bool:
        now = monotonic()
        if now - self._last_alert_at < self.debounce_seconds:
            return False

        self.audio_backend.play_alert()
        self.notification_backend.send(
            title="Task expired",
            body=f"{event.title} has reached its deadline.",
        )
        self._last_alert_at = now
        return True

    def notify_task_started(self, title: str, remaining_seconds: int) -> None:
        minutes = max(1, remaining_seconds // 60)
        self.notification_backend.send(
            title="Task started",
            body=f"{title} - {minutes} minute(s) remaining.",
        )
