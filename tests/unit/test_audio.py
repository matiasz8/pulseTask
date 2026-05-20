from pathlib import Path
from unittest.mock import patch

from pulse_task.system.audio import AudioBackend


@patch("pulse_task.system.audio.subprocess.run")
@patch("pulse_task.system.audio.shutil.which")
def test_play_alert_uses_double_play_when_strong_enabled(
    which_mock,
    run_mock,
) -> None:
    which_mock.side_effect = lambda name: "/usr/bin/paplay" if name == "paplay" else None

    with patch.object(Path, "exists", return_value=True):
        backend = AudioBackend(strong_final_sound=True)
        backend.play_alert()

    assert run_mock.call_count == 2


@patch("pulse_task.system.audio.subprocess.run")
@patch("pulse_task.system.audio.shutil.which")
def test_play_alert_uses_single_play_when_strong_disabled(
    which_mock,
    run_mock,
) -> None:
    which_mock.side_effect = lambda name: "/usr/bin/paplay" if name == "paplay" else None

    with patch.object(Path, "exists", return_value=True):
        backend = AudioBackend(strong_final_sound=False)
        backend.play_alert()

    assert run_mock.call_count == 1
