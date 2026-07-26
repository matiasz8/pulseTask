"""CountdownWidget - Custom countdown display for PulseTask V2.

Provides multiple sizes and visual states for the countdown timer.
"""

from __future__ import annotations

import math
from enum import Enum

from gi.repository import Gdk, Gtk

try:
    import cairo
except ImportError:
    cairo = None  # type: ignore[assignment]


class CountdownSize(Enum):
    """Size variants for the countdown display."""

    XS = "xs"  # 14px - for status bar, compact overlay
    SM = "sm"  # 18px - for compact overlay
    MD = "md"  # 32px - for cards, normal overlay
    LG = "lg"  # 48px - for focus view header
    XL = "xl"  # 64px - for focus view main


class CountdownStatus(Enum):
    """Visual states for the countdown."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    EXPIRED = "expired"
    COMPLETED = "completed"


class CountdownWidget(Gtk.DrawingArea):
    """Custom countdown display with visual states.

    Features:
    - Multiple size variants (XS, SM, MD, LG, XL)
    - Visual state indicators (running, paused, expired, etc.)
    - Optional progress ring
    - High contrast accessibility support
    - Reduced motion support
    """

    def __init__(
        self,
        size: CountdownSize = CountdownSize.MD,
        show_progress: bool = True,
    ) -> None:
        super().__init__()

        self._size = size
        self._show_progress = show_progress
        self._elapsed = 0
        self._duration = 0
        self._status = CountdownStatus.PENDING
        self._remaining_text = "00:00"
        self._progress = 0.0
        self._progress_animation = 0.0

        # Set up drawing
        self.set_draw_func(self._draw)

        # Update size based on variant
        self._update_size_request()

        # Animation timer for smooth progress
        self._animation_timeout_id: int | None = None

    @property
    def elapsed(self) -> int:
        return self._elapsed

    @elapsed.setter
    def elapsed(self, value: int) -> None:
        self._elapsed = max(0, value)
        self._update_display()

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value: int) -> None:
        self._duration = max(1, value)  # Avoid division by zero
        self._update_display()

    @property
    def status(self) -> CountdownStatus:
        return self._status

    @status.setter
    def status(self, value: CountdownStatus) -> None:
        self._status = value
        self.queue_draw()

    @property
    def size(self) -> CountdownSize:
        return self._size

    @size.setter
    def size(self, value: CountdownSize) -> None:
        self._size = value
        self._update_size_request()
        self.queue_draw()

    @property
    def show_progress(self) -> bool:
        return self._show_progress

    @show_progress.setter
    def show_progress(self, value: bool) -> None:
        self._show_progress = value
        self._update_size_request()
        self.queue_draw()

    def _update_size_request(self) -> None:
        """Update widget size based on countdown size variant."""
        sizes = {
            CountdownSize.XS: (80, 32),
            CountdownSize.SM: (100, 40),
            CountdownSize.MD: (160, 56),
            CountdownSize.LG: (200, 72),
            CountdownSize.XL: (260, 96),
        }
        width, height = sizes.get(self._size, (160, 56))
        self.set_size_request(width, height)

    def _update_display(self) -> None:
        """Update the time text and progress."""
        remaining = self._duration - self._elapsed

        if self._duration > 0:
            self._progress = min(1.0, self._elapsed / self._duration)
        else:
            self._progress = 0.0

        # Format time string
        self._remaining_text = self._format_time(abs(remaining))

        # Queue redraw
        self.queue_draw()

    def _format_time(self, seconds: int) -> str:
        """Format seconds into MM:SS or HH:MM:SS."""
        if seconds < 0:
            seconds = 0

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _get_font_size(self) -> int:
        """Get font size based on countdown size variant."""
        sizes = {
            CountdownSize.XS: 14,
            CountdownSize.SM: 18,
            CountdownSize.MD: 32,
            CountdownSize.LG: 48,
            CountdownSize.XL: 64,
        }
        return sizes.get(self._size, 32)

    def _get_color_for_status(self) -> Gdk.RGBA:
        """Get the appropriate color for the current status."""
        colors = {
            CountdownStatus.PENDING: "#6b7280",  # Gray
            CountdownStatus.RUNNING: "#2ec27e",  # Green
            CountdownStatus.PAUSED: "#e5a11c",  # Amber
            CountdownStatus.EXPIRED: "#e01b24",  # Red
            CountdownStatus.COMPLETED: "#33d17a",  # Green (different shade)
        }

        color_str = colors.get(self._status, "#6b7280")
        rgba = Gdk.RGBA()
        rgba.parse(color_str)
        return rgba

    def _draw(self, area: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int) -> None:
        """Draw the countdown display."""

        # Get colors
        color = self._get_color_for_status()

        # Calculate dimensions
        font_size = self._get_font_size()

        # Draw progress ring (if enabled)
        large_sizes = {CountdownSize.MD, CountdownSize.LG, CountdownSize.XL}
        if self._show_progress and self._size in large_sizes:
            self._draw_progress_ring(cr, width, height, color)

        # Draw time text
        self._draw_time_text(cr, width, height, color, font_size)

    def _draw_progress_ring(
        self,
        cr: cairo.Context,
        width: int,
        height: int,
        color: Gdk.RGBA,
    ) -> None:
        """Draw a circular progress ring around the countdown."""

        # Calculate ring dimensions
        ring_width = 4 if self._size == CountdownSize.MD else 6
        radius = min(width, height) / 2 - ring_width
        center_x = width / 2
        center_y = height / 2

        # Draw background circle (track)
        cr.set_line_width(ring_width)
        cr.set_source_rgba(color.red, color.green, color.blue, 0.15)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.stroke()

        # Draw progress arc
        if self._progress > 0:
            cr.set_line_width(ring_width)
            cr.set_source_rgba(color.red, color.green, color.blue, 0.8)
            # Start from top (-π/2), go clockwise
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * self._progress)
            cr.arc(center_x, center_y, radius, start_angle, end_angle)
            cr.stroke()

    def _draw_time_text(
        self,
        cr: cairo.Context,
        width: int,
        height: int,
        color: Gdk.RGBA,
        font_size: int,
    ) -> None:
        """Draw the countdown time text."""
        import cairo

        # Set font
        cr.select_font_face(
            "JetBrains Mono, Cascadia Code, Fira Code, monospace",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD,
        )
        cr.set_font_size(font_size)

        # Calculate text position (centered)
        extents = cr.text_extents(self._remaining_text)
        text_width = extents.width
        text_height = extents.height

        text_x = (width - text_width) / 2
        text_y = (height + text_height) / 2  # Center vertically

        # Draw text
        cr.set_source_rgba(color.red, color.green, color.blue, 1.0)
        cr.move_to(text_x, text_y)
        cr.show_text(self._remaining_text)

    def update(self, elapsed: int, duration: int, status: CountdownStatus) -> None:
        """Update all countdown properties at once."""
        self._elapsed = elapsed
        self._duration = max(1, duration)
        self._status = status
        self._update_display()


def create_countdown_widget(
    size: str = "md",
    show_progress: bool = True,
) -> CountdownWidget:
    """Factory function to create a CountdownWidget.

    Args:
        size: Size variant string ("xs", "sm", "md", "lg", "xl")
        show_progress: Whether to show the progress ring

    Returns:
        Configured CountdownWidget instance
    """
    size_enum = CountdownSize(size)
    return CountdownWidget(size=size_enum, show_progress=show_progress)
