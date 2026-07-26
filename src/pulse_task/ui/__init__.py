"""UI package for PulseTask V2."""

from pulse_task.ui.compact_overlay import CompactOverlay
from pulse_task.ui.countdown_widget import CountdownSize, CountdownStatus, CountdownWidget
from pulse_task.ui.focus_view import FocusView
from pulse_task.ui.stats_view import StatsView
from pulse_task.ui.styles import (
    STATUS_COLORS,
    ButtonStyle,
    OverlayMode,
    StatusBadgeStyle,
    TaskCardStyle,
    get_status_color,
    get_status_css_class,
    get_task_card_css_class,
)
from pulse_task.ui.task_card import TaskCard

__all__ = [
    "CountdownWidget",
    "CountdownSize",
    "CountdownStatus",
    "TaskCard",
    "FocusView",
    "CompactOverlay",
    "StatsView",
    "TaskCardStyle",
    "StatusBadgeStyle",
    "ButtonStyle",
    "OverlayMode",
    "STATUS_COLORS",
    "get_status_color",
    "get_status_css_class",
    "get_task_card_css_class",
]


def get_v2_css_path() -> str:
    """Return the path to the V2 CSS styles file."""
    from pathlib import Path

    return str(Path(__file__).parent / "styles_v2.css")
