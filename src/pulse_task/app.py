from pathlib import Path
import os
import sys

from pulse_task.core.alerts import AlertManager
from pulse_task.core.group_service import GroupService
from pulse_task.core.metrics import LocalMetrics
from pulse_task.core.persistence import TaskRepository
from pulse_task.core.preferences import PreferencesRepository
from pulse_task.core.service import TaskService
from pulse_task.system.audio import AudioBackend
from pulse_task.system.search_provider import SearchProvider
from pulse_task.ui.desktop import launch_desktop_ui

try:
    import gi  # type: ignore[import-untyped]

    gi.require_version("Gio", "2.0")
    from gi.repository import Gio, GLib  # type: ignore[import-untyped]
except (ImportError, ValueError):
    Gio = None
    GLib = None


def _setup_gsettings_path() -> None:
    """Setup GSettings schema path for development/local usage."""
    if GLib is None:
        return
    
    # Check if schema is in development directory
    dev_schema_dir = Path(__file__).parent.parent.parent / "data"
    if dev_schema_dir.exists() and (dev_schema_dir / "gschemas.compiled").exists():
        schema_path = str(dev_schema_dir)
        try:
            # Get current search path
            schema_search_path = GLib.get_system_data_dirs()
            # Prepend development schema directory
            GLib.set_user_data_dirs(schema_path)
        except Exception:
            # If that fails, just set environment variable
            os.environ["GSETTINGS_SCHEMA_DIR"] = schema_path


def _resolve_task_title(service: TaskService, task_id: str) -> str | None:
    """Resolve a task title for search provider metadata."""
    try:
        return service.get_task(task_id).title
    except ValueError:
        return None


class _SettingsAdapter:
    """Minimal adapter exposing Gio.Settings-like methods from user preferences."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def get_boolean(self, key: str) -> bool:
        """Return the enabled state for the search provider key."""
        return self.enabled if key == "search-provider-enabled" else True

    def list_keys(self) -> list[str]:
        """Return the supported key list."""
        return ["search-provider-enabled"]


def _search_provider_settings() -> object:
    """Load GSettings when available and fall back to the local adapter otherwise."""
    if Gio is None:
        return _SettingsAdapter(enabled=True)
    try:
        return Gio.Settings.new("org.gnome.Pulse")
    except Exception:
        return _SettingsAdapter(enabled=True)


def run() -> int:
    """Application entrypoint."""
    _setup_gsettings_path()
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

    search_provider = SearchProvider(
        GroupService(repository.database),
        task_title_resolver=lambda task_id: _resolve_task_title(service, task_id),
        settings=_search_provider_settings(),
    )
    search_provider.register()
    try:
        return launch_desktop_ui(
            service,
            preferences_repo,
            preferences,
            search_provider=search_provider,
        )
    finally:
        search_provider.unregister()
