from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class UserPreferences:
    default_duration_minutes: int = 20
    show_archived_by_default: bool = False
    strong_final_sound: bool = False
    close_to_tray: bool = True

    def normalized(self) -> UserPreferences:
        minutes = max(1, min(480, int(self.default_duration_minutes)))
        return UserPreferences(
            default_duration_minutes=minutes,
            show_archived_by_default=bool(self.show_archived_by_default),
            strong_final_sound=bool(self.strong_final_sound),
            close_to_tray=bool(self.close_to_tray),
        )


class PreferencesRepository:
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> UserPreferences:
        if not self.file_path.exists():
            return UserPreferences()

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return UserPreferences()

        if not isinstance(raw, dict):
            return UserPreferences()

        prefs = UserPreferences(
            default_duration_minutes=raw.get("default_duration_minutes", 20),
            show_archived_by_default=raw.get("show_archived_by_default", False),
            strong_final_sound=raw.get("strong_final_sound", False),
            close_to_tray=raw.get("close_to_tray", True),
        )
        return prefs.normalized()

    def save(self, preferences: UserPreferences) -> None:
        normalized = preferences.normalized()
        self.file_path.write_text(
            json.dumps(asdict(normalized), indent=2, sort_keys=True),
            encoding="utf-8",
        )
