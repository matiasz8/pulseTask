from pathlib import Path

from pulse_task.core.alerts import AlertManager
from pulse_task.core.metrics import LocalMetrics
from pulse_task.core.persistence import TaskRepository
from pulse_task.core.preferences import PreferencesRepository
from pulse_task.core.service import TaskService
from pulse_task.system.audio import AudioBackend
from pulse_task.ui.desktop import launch_desktop_ui


def run() -> int:
    """Application entrypoint."""
    data_dir = Path.home() / ".local" / "share" / "pulsetask"
    data_dir.mkdir(parents=True, exist_ok=True)
    config_dir = Path.home() / ".config" / "pulsetask"
    preferences_repo = PreferencesRepository(config_dir / "preferences.json")
    preferences = preferences_repo.load()

    repository = TaskRepository(data_dir / "tasks.db")
    alert_manager = AlertManager(
        audio_backend=AudioBackend(preferences.strong_final_sound),
        notifications_enabled=preferences.notifications_enabled,
    )
    metrics = LocalMetrics(data_dir / "metrics.json")
    service = TaskService(repository=repository, alert_manager=alert_manager, metrics=metrics)
    service.recover_running_tasks()

    return launch_desktop_ui(service, preferences_repo, preferences)
