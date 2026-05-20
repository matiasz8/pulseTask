from pulse_task.system.tray import TrayCapabilities


def test_tray_capabilities_dataclass_defaults() -> None:
    caps = TrayCapabilities(available=False, reason="missing")
    assert caps.available is False
    assert caps.reason == "missing"
