from pathlib import Path

from pulse_task.core.persistence import TaskRepository
from pulse_task.core.service import TaskService
from pulse_task.system.tray import detect_tray_capabilities
from pulse_task.ui.desktop import launch_desktop_ui


def run() -> int:
    """Application entrypoint."""
    data_dir = Path.home() / ".local" / "share" / "pulsetask"
    data_dir.mkdir(parents=True, exist_ok=True)

    repository = TaskRepository(data_dir / "tasks.db")
    service = TaskService(repository=repository)
    service.recover_running_tasks()

    tray = detect_tray_capabilities()
    if not tray.available:
        print("Tray countdown support not detected; running window mode only.")

    return launch_desktop_ui(service)
