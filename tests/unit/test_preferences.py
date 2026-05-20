from pathlib import Path

from pulse_task.core.preferences import PreferencesRepository, UserPreferences


def test_preferences_defaults_when_file_missing(tmp_path: Path) -> None:
    repo = PreferencesRepository(tmp_path / "preferences.json")

    loaded = repo.load()

    assert loaded == UserPreferences()


def test_preferences_roundtrip(tmp_path: Path) -> None:
    repo = PreferencesRepository(tmp_path / "preferences.json")
    prefs = UserPreferences(
        default_duration_minutes=35,
        show_archived_by_default=True,
        strong_final_sound=True,
        close_to_tray=False,
    )

    repo.save(prefs)
    loaded = repo.load()

    assert loaded.default_duration_minutes == 35
    assert loaded.show_archived_by_default is True
    assert loaded.strong_final_sound is True
    assert loaded.close_to_tray is False


def test_preferences_normalizes_out_of_range_minutes(tmp_path: Path) -> None:
    repo = PreferencesRepository(tmp_path / "preferences.json")
    prefs = UserPreferences(default_duration_minutes=1000)

    repo.save(prefs)
    loaded = repo.load()

    assert loaded.default_duration_minutes == 480
