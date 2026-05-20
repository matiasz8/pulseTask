from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AudioBackend:
    """Simple audio backend for Linux desktop environments.

    Uses canberra-gtk-play when available.
    """

    def play_alert(self) -> None:
        paplay = shutil.which("paplay")
        alarm_file = Path("/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga")
        if paplay is not None and alarm_file.exists():
            for _ in range(2):
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
        for _ in range(2):
            subprocess.run(
                [
                    canberra,
                    "--id",
                    "message-warning",
                    "--description",
                    "PulseTask deadline reached",
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
