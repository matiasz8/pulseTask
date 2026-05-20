from pulse_task.core.alerts import AlertEvent, AlertManager


class _FakeAudio:
    def __init__(self) -> None:
        self.calls = 0

    def play_alert(self) -> None:
        self.calls += 1


class _FakeNotify:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def send(self, title: str, body: str) -> None:
        self.calls.append((title, body))


def test_alert_manager_sends_audio_and_notification() -> None:
    audio = _FakeAudio()
    notify = _FakeNotify()
    manager = AlertManager(audio_backend=audio, notification_backend=notify, debounce_seconds=0)

    emitted = manager.alert_task_expired(AlertEvent(task_id="1", title="Deploy"))

    assert emitted is True
    assert audio.calls == 1
    assert notify.calls == [("Task expired", "Deploy has reached its deadline.")]


def test_alert_manager_debounces_quick_repeats() -> None:
    audio = _FakeAudio()
    notify = _FakeNotify()
    manager = AlertManager(audio_backend=audio, notification_backend=notify, debounce_seconds=3600)

    first = manager.alert_task_expired(AlertEvent(task_id="1", title="Task A"))
    second = manager.alert_task_expired(AlertEvent(task_id="1", title="Task A"))

    assert first is True
    assert second is False
    assert audio.calls == 1
    assert len(notify.calls) == 1
