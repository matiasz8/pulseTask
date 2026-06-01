"""System integration package for PulseTask."""

from pulse_task.system.notifications import NotificationManager
from pulse_task.system.quick_settings import QuickSettingsWidget
from pulse_task.system.shortcuts import GlobalShortcuts

__all__ = ["NotificationManager", "QuickSettingsWidget", "GlobalShortcuts"]
