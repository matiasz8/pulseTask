"""StatsView - Advanced statistics dashboard for PulseTask V2.

Displays operational metrics with trend indicators, time range selection,
and summary insights. Based on the V2 React design (stats-dashboard.tsx).
"""

from __future__ import annotations

from gi.repository import Gtk, Pango

from pulse_task.core.stats import GroupStatsService

# ---------------------------------------------------------------------------
# Metric card widget
# ---------------------------------------------------------------------------


class MetricCard(Gtk.Box):
    """A single metric card displaying a value, label, and optional trend.

    Layout:
    ┌───────────────────────┐
    │ [icon]          [trend]│
    │   85%                  │
    │   Completion Rate      │
    │   Tasks finished ...   │
    └───────────────────────┘
    """

    def __init__(
        self,
        label: str,
        value: str,
        description: str = "",
        icon_name: str = "dialog-information-symbolic",
        trend: str = "neutral",
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.add_css_class("metric-card")

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_size_request(200, -1)

        # Top row: icon + trend
        top_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )

        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(20)
        icon.add_css_class("dim-label")
        top_row.append(icon)

        top_row.set_hexpand(True)

        if trend != "neutral":
            trend_label = Gtk.Label()
            if trend == "up":
                trend_label.set_markup('<span foreground="#33d17a" weight="bold">↑</span>')
            else:
                trend_label.set_markup('<span foreground="#e01b24" weight="bold">↓</span>')
            top_row.append(trend_label)

        self.append(top_row)

        # Value
        value_label = Gtk.Label(xalign=0)
        value_label.set_markup(
            f'<span size="xx-large" weight="bold" font_family="monospace">{value}</span>'
        )
        value_label.set_margin_top(4)
        self.append(value_label)

        # Label
        label_widget = Gtk.Label(xalign=0, label=label)
        label_widget.set_margin_top(2)
        self.append(label_widget)

        # Description
        if description:
            desc_widget = Gtk.Label(xalign=0, label=description)
            desc_widget.add_css_class("dim-label")
            desc_widget.set_ellipsize(Pango.EllipsizeMode.END)
            desc_widget.set_max_width_chars(40)
            desc_widget.set_wrap(True)
            self.append(desc_widget)


# ---------------------------------------------------------------------------
# Time range selector
# ---------------------------------------------------------------------------


class TimeRangeSelector(Gtk.Box):
    """Button group for selecting time range: Today / 7 Days / 30 Days."""

    def __init__(self, on_change: callable | None = None) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.set_halign(Gtk.Align.CENTER)
        self.set_margin_bottom(24)

        self._on_change = on_change
        self._buttons: dict[str, Gtk.ToggleButton] = {}

        ranges = [("Today", 1), ("7 Days", 7), ("30 Days", 30)]

        for label, days in ranges:
            btn = Gtk.ToggleButton(label=label)
            btn.add_css_class("flat")
            btn.connect("toggled", self._on_toggled, days)
            self._buttons[label] = btn
            self.append(btn)

        # Default to 7 days
        if "7 Days" in self._buttons:
            self._buttons["7 Days"].set_active(True)

    def _on_toggled(self, button: Gtk.ToggleButton, days: int) -> None:
        if not button.get_active():
            return
        # Deactivate siblings
        for other in self._buttons.values():
            if other is not button:
                other.set_active(False)
        if self._on_change:
            self._on_change(days)


# ---------------------------------------------------------------------------
# Stats View
# ---------------------------------------------------------------------------


class StatsView(Gtk.Box):
    """Statistics dashboard showing operational metrics.

    Features:
    - 6 metric cards with trend indicators
    - Time range selector (Today / 7d / 30d)
    - Summary insight text
    - Weekly heatmap
    - Export controls
    """

    def __init__(self, stats_service: GroupStatsService | None = None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.stats_service = stats_service

        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.add_css_class("stats-view")

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title = Gtk.Label(xalign=0)
        title.set_markup('<span size="x-large" weight="bold">Operational Metrics</span>')
        header.append(title)

        subtitle = Gtk.Label(xalign=0, label="Focus performance and execution patterns")
        subtitle.add_css_class("dim-label")
        header.append(subtitle)

        self.append(header)

        # Time range selector
        self._time_range = TimeRangeSelector(on_change=self._on_range_changed)
        self.append(self._time_range)

        # Metric cards grid
        self._grid = Gtk.Grid()
        self._grid.set_column_spacing(16)
        self._grid.set_row_spacing(16)
        self._grid.set_halign(Gtk.Align.FILL)
        self.append(self._grid)

        # Summary
        self._summary_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )
        self._summary_box.set_margin_top(24)
        self._summary_box.add_css_class("stats-section")
        self.append(self._summary_box)

        # Heatmap
        self._heatmap_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
        )
        self._heatmap_box.set_margin_top(16)
        self._heatmap_box.add_css_class("stats-section")
        self.append(self._heatmap_box)

        # Build initial view
        self._current_days = 7
        self._refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh_data(self) -> None:
        """Force a data refresh."""
        self._refresh()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_range_changed(self, days: int) -> None:
        self._current_days = days
        self._refresh()

    def _refresh(self) -> None:
        """Rebuild the metric cards and summary from current data."""
        # Clear grid
        child = self._grid.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._grid.remove(child)
            child = next_child

        # Clear summary
        child = self._summary_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._summary_box.remove(child)
            child = next_child

        # Clear heatmap
        child = self._heatmap_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._heatmap_box.remove(child)
            child = next_child

        # Build metric cards from period stats
        if self.stats_service is not None:
            period = self.stats_service.get_period_stats(self._current_days)
            self._build_metric_cards_from_period(period)
            self._build_heatmap()
        else:
            # No data available — show placeholder cards
            self._build_placeholder_cards()

        # Build summary
        self._build_summary()

    def _build_metric_cards_from_period(self, period) -> None:  # type: ignore[no-untyped-def]
        """Build 6 metric cards from period stats."""
        cards = [
            MetricCard(
                label="Completion Rate",
                value=f"{period.completion_rate:.0%}",
                description="Groups completed successfully",
                icon_name="object-select-symbolic",
                trend="up" if period.completion_rate >= 0.7 else "down",
            ),
            MetricCard(
                label="Groups Executed",
                value=str(period.groups_executed),
                description=f"Over {period.period_days} days",
                icon_name="media-playback-start-symbolic",
                trend="neutral",
            ),
            MetricCard(
                label="Tasks Completed",
                value=str(period.tasks_completed),
                description="Total tasks finished",
                icon_name="task-complete-symbolic",
                trend="neutral",
            ),
            MetricCard(
                label="Focus Time",
                value=self._format_duration(period.total_focus_time_seconds),
                description="Total focused time",
                icon_name="preferences-system-time-symbolic",
                trend="neutral",
            ),
            MetricCard(
                label="Avg Group Duration",
                value=self._format_duration(period.avg_group_duration_seconds),
                description="Average session length",
                icon_name="duration-symbolic",
                trend="neutral",
            ),
            MetricCard(
                label="Interruption Rate",
                value=f"{period.interruption_rate:.1f}",
                description="Skips per group",
                icon_name="process-stop-symbolic",
                trend="down" if period.interruption_rate > 1 else "up",
            ),
        ]

        for i, card in enumerate(cards):
            row = i // 3
            col = i % 3
            self._grid.attach(card, col, row, 1, 1)

    def _build_placeholder_cards(self) -> None:
        """Show placeholder cards when no stats service is available."""
        placeholders = [
            ("Completion Rate", "—", "Connect to data source"),
            ("Groups Executed", "—", "Connect to data source"),
            ("Tasks Completed", "—", "Connect to data source"),
            ("Focus Time", "—", "Connect to data source"),
            ("Avg Group Duration", "—", "Connect to data source"),
            ("Interruption Rate", "—", "Connect to data source"),
        ]
        for i, (label, value, desc) in enumerate(placeholders):
            card = MetricCard(label=label, value=value, description=desc)
            row = i // 3
            col = i % 3
            self._grid.attach(card, col, row, 1, 1)

    def _build_summary(self) -> None:
        """Build the summary insight section."""
        heading = Gtk.Label(xalign=0, label="Summary")
        heading.add_css_class("heading-3")
        self._summary_box.append(heading)

        if self.stats_service is None:
            text = "Start completing tasks to see your operational metrics."
        else:
            period = self.stats_service.get_period_stats(self._current_days)
            if period.groups_executed == 0:
                text = "Start completing tasks to see your operational metrics."
            elif period.completion_rate >= 0.7:
                text = (
                    "Strong execution discipline. "
                    "Your completion rate and focused sessions are consistent."
                )
            elif period.completion_rate >= 0.4:
                text = (
                    "Moderate performance. Consider reducing pauses and improving time estimates."
                )
            else:
                text = (
                    "Execution needs improvement. "
                    "Try shorter task durations and minimize interruptions."
                )

        summary_label = Gtk.Label(xalign=0, label=text)
        summary_label.set_wrap(True)
        summary_label.add_css_class("dim-label")
        self._summary_box.append(summary_label)

    def _build_heatmap(self) -> None:
        """Build the weekly activity heatmap."""
        if self.stats_service is None:
            return

        heading = Gtk.Label(xalign=0, label="Weekly Activity")
        heading.add_css_class("heading-3")
        self._heatmap_box.append(heading)

        heatmap = self.stats_service.get_focus_heatmap(days=min(self._current_days, 7))

        row_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
        )
        row_box.set_halign(Gtk.Align.START)

        for day, intensity in heatmap.items():
            day_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=4,
            )

            # Color block
            intensity_level = min(4, int(intensity * 4))
            block = Gtk.Box()
            block.set_size_request(32, 32)
            block.set_css_classes([f"heatmap-{intensity_level}", "heatmap-block"])
            day_box.append(block)

            day_label = Gtk.Label(label=day[:3])
            day_label.add_css_class("dim-label")
            day_box.append(day_label)

            row_box.append(day_box)

        self._heatmap_box.append(row_box)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds to human-readable duration."""
        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            return f"{seconds // 60}m"
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
