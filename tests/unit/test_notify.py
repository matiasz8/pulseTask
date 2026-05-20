from unittest.mock import patch

from pulse_task.system.notify import NotificationBackend


def test_notify_send_uses_pulsetask_app_name() -> None:
    backend = NotificationBackend()

    with patch("pulse_task.system.notify.shutil.which", return_value="/usr/bin/notify-send"):
        with patch("pulse_task.system.notify.subprocess.run") as run:
            backend.send("Task started", "Focus block - 25 minute(s) remaining.")

    args = run.call_args.args[0]
    assert args[:3] == ["/usr/bin/notify-send", "-a", "PulseTask"]
    assert args[3] == "Task started"
