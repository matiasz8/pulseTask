"""D-Bus service integration for PulseTask.

Provides org.gnome.Pulse D-Bus service for system integration:
- Quick Settings control
- Shell notifications with actions
- Global keyboard shortcuts
- Search provider integration
"""

from .service import DBusService

__all__ = ["DBusService"]
