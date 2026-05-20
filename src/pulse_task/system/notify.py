from __future__ import annotations

import shutil
import subprocess


class NotificationBackend:
    """Desktop notification backend using notify-send when available."""

    def send(self, title: str, body: str) -> None:
        command = shutil.which("notify-send")
        if command is None:
            return
        subprocess.run(
            [command, "-a", "PulseTask", title, body],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
