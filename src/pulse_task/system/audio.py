from __future__ import annotations

import shutil
import subprocess


class AudioBackend:
    """Simple audio backend for Linux desktop environments.

    Uses canberra-gtk-play when available.
    """

    def play_alert(self) -> None:
        command = shutil.which("canberra-gtk-play")
        if command is None:
            return
        subprocess.run(
            [command, "--id", "message-warning", "--description", "PulseTask deadline reached"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
