"""Style constants and helpers for PulseTask V2."""

from __future__ import annotations

from enum import Enum


class TaskCardStyle(Enum):
    """CSS class names for task card states."""

    BASE = "task-card"
    ACTIVE = "task-card-active"
    RUNNING = "task-card-running"
    PAUSED = "task-card-paused"
    PENDING = "task-card-pending"
    EXPIRED = "task-card-expired"
    COMPLETED = "task-card-completed"
    ARCHIVED = "task-card-archived"


class StatusBadgeStyle(Enum):
    """CSS class names for status badges."""

    BASE = "status-badge"
    RUNNING = "status-running"
    PAUSED = "status-paused"
    PENDING = "status-pending"
    EXPIRED = "status-expired"
    COMPLETED = "status-completed"
    ARCHIVED = "status-archived"


class ButtonStyle(Enum):
    """CSS class names for buttons."""

    PRIMARY = "btn-primary"
    SECONDARY = "btn-secondary"
    SUCCESS = "btn-success"
    DANGER = "btn-danger"
    GHOST = "btn-ghost"
    ICON = "btn-icon"
    PILL = "pill"


class OverlayMode(Enum):
    """Overlay density mode constants."""

    NORMAL = "normal"
    COMPACT = "compact"
    ULTRACOMPACT = "ultracompact"


# Status color constants (matching CSS)
STATUS_COLORS = {
    "pending": "#6b7280",
    "running": "#2ec27e",
    "paused": "#e5a11c",
    "expired": "#e01b24",
    "completed": "#33d17a",
    "archived": "#9ca3af",
}


def get_status_color(status: str) -> str:
    """Get the hex color for a task status."""
    return STATUS_COLORS.get(status, "#6b7280")


def get_status_css_class(status: str) -> str:
    """Get the CSS class for a task status."""
    return f"status-{status}"


def get_task_card_css_class(status: str, is_active: bool = False) -> str:
    """Get the CSS class for a task card."""
    classes = ["task-card", f"task-card-{status}"]
    if is_active:
        classes.append("task-card-active")
    return " ".join(classes)
