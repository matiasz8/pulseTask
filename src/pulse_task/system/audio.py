from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AudioBackend:
    """Simple audio backend for Linux desktop environments.

    Uses canberra-gtk-play when available.
    """

    def __init__(self, strong_final_sound: bool = False) -> None:
        self.strong_final_sound = strong_final_sound

    def set_strong_final_sound(self, enabled: bool) -> None:
        self.strong_final_sound = enabled

    def play_alert(self) -> None:
        paplay = shutil.which("paplay")
        alarm_file = Path("/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga")
        if paplay is not None and alarm_file.exists():
            repeats = 2 if self.strong_final_sound else 1
            for _ in range(repeats):
                subprocess.run(
                    [paplay, str(alarm_file)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return

        canberra = shutil.which("canberra-gtk-play")
        if canberra is None:
            return
        alert_id = "complete" if self.strong_final_sound else "message-warning"
        subprocess.run(
            [
                canberra,
                "--id",
                alert_id,
                "--description",
                "PulseTask final alert",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def play_countdown_cue(self) -> None:
        canberra = shutil.which("canberra-gtk-play")
        if canberra is None:
            return
        subprocess.run(
            [
                canberra,
                "--id",
                "bell-terminal",
                "--description",
                "PulseTask countdown cue",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
