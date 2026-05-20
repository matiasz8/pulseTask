from pulse_task.core.alerts import AlertEvent, AlertManager


class _FakeAudio:
    def __init__(self) -> None:
        self.calls = 0
        self.cue_calls = 0

    def play_alert(self) -> None:
        self.calls += 1

    def play_countdown_cue(self) -> None:
        self.cue_calls += 1


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


def test_alert_manager_notifies_task_started() -> None:
    audio = _FakeAudio()
    notify = _FakeNotify()
    manager = AlertManager(audio_backend=audio, notification_backend=notify, debounce_seconds=0)

    manager.notify_task_started("Focus block", remaining_seconds=1500)

    assert audio.calls == 0
    assert notify.calls == [("Task started", "Focus block - 25 min remaining.")]


def test_alert_manager_notifies_task_started_with_hours() -> None:
    notify = _FakeNotify()
    manager = AlertManager(
        audio_backend=_FakeAudio(),
        notification_backend=notify,
        debounce_seconds=0,
    )

    manager.notify_task_started("Deep session", remaining_seconds=4200)

    assert notify.calls == [("Task started", "Deep session - 1h and 10 min remaining.")]


def test_alert_manager_notifies_task_finished() -> None:
    notify = _FakeNotify()
    manager = AlertManager(
        audio_backend=_FakeAudio(),
        notification_backend=notify,
        debounce_seconds=0,
    )

    manager.notify_task_finished("Deep session")

    assert notify.calls == [
        ("Task finished", "Deep session finished. Starting next task if available."),
    ]


def test_countdown_cue_only_for_last_three_seconds_and_without_duplicates() -> None:
    audio = _FakeAudio()
    manager = AlertManager(
        audio_backend=audio,
        notification_backend=_FakeNotify(),
        debounce_seconds=0,
    )

    assert manager.maybe_play_countdown_cue("task-1", 6) is False
    assert manager.maybe_play_countdown_cue("task-1", 4) is False
    assert manager.maybe_play_countdown_cue("task-1", 3) is True
    assert manager.maybe_play_countdown_cue("task-1", 3) is False
    assert manager.maybe_play_countdown_cue("task-1", 2) is True
    assert audio.cue_calls == 2
