"""Statistics dashboard window for PulseTask."""
# mypy: disable-error-code=misc

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import gi  # type: ignore[import-untyped]

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, Gtk  # type: ignore[import-untyped]  # noqa: E402

from pulse_task.core.group_service import GroupService  # noqa: E402
from pulse_task.core.stats import DailyGroupStats, GroupStatsService  # noqa: E402

PERIOD_DAYS: dict[str, int] = {
    "today": 1,
    "week": 7,
    "month": 30,
}
PERIOD_LABELS: dict[str, str] = {
    "today": "Today",
    "week": "This Week",
    "month": "This Month",
}
PERIOD_COMPARISON_LABELS: dict[str, str] = {
    "today": "yesterday",
    "week": "last week",
    "month": "last month",
}


@dataclass(slots=True)
class MetricData:
    """Display-ready metric information for a card."""

    title: str
    value: str
    unit: str
    detail: str
    indicator_class: str
    trend: str = ""


@dataclass(slots=True)
class ChartRow:
    """Single activity chart row."""

    label: str
    value_seconds: int


@dataclass(slots=True)
class DashboardData:
    """Aggregated data used to refresh the dashboard."""

    metrics: dict[str, MetricData]
    chart_rows: list[ChartRow]


@dataclass(slots=True)
class LegacyAggregate:
    """Aggregated legacy stats for a slice of daily data."""

    groups_executed: int
    tasks_completed: int
    total_focus_time_seconds: int
    interruptions: int


class MetricCard(Gtk.Box):
    """Reusable card used by the statistics grid."""

    def __init__(self, title: str) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add_css_class("stats-card")
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(6)
        self.set_margin_end(6)

        self.title_label = Gtk.Label(label=title)
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_xalign(0.0)
        self.title_label.add_css_class("stats-label")
        self.append(self.title_label)

        value_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        value_box.set_halign(Gtk.Align.START)
        self.value_label = Gtk.Label(label="--")
        self.value_label.set_xalign(0.0)
        self.value_label.add_css_class("stats-value")
        value_box.append(self.value_label)

        self.unit_label = Gtk.Label(label="")
        self.unit_label.set_xalign(0.0)
        self.unit_label.add_css_class("stats-unit")
        value_box.append(self.unit_label)
        self.append(value_box)

        self.detail_label = Gtk.Label(label="")
        self.detail_label.set_xalign(0.0)
        self.detail_label.set_wrap(True)
        self.detail_label.add_css_class("caption")
        self.append(self.detail_label)

        self.indicator_label = Gtk.Label(label="")
        self.indicator_label.set_halign(Gtk.Align.START)
        self.indicator_label.add_css_class("stats-indicator")
        self.append(self.indicator_label)

        self.trend_label = Gtk.Label(label="")
        self.trend_label.set_xalign(0.0)
        self.trend_label.set_wrap(True)
        self.trend_label.add_css_class("stats-trend")
        self.append(self.trend_label)

    def update(self, metric: MetricData) -> None:
        """Refresh the card contents."""
        self.title_label.set_label(metric.title)
        self.value_label.set_label(metric.value)
        self.unit_label.set_label(metric.unit)
        self.unit_label.set_visible(bool(metric.unit))
        self.detail_label.set_label(metric.detail)
        self.indicator_label.set_label(self._indicator_label(metric.indicator_class))
        self._set_indicator_class(metric.indicator_class)
        self.trend_label.set_label(metric.trend)
        self.trend_label.set_visible(bool(metric.trend))

    def _set_indicator_class(self, indicator_class: str) -> None:
        for css_class in (
            "stats-indicator-green",
            "stats-indicator-yellow",
            "stats-indicator-red",
        ):
            self.indicator_label.remove_css_class(css_class)
            self.remove_css_class(css_class)
        self.indicator_label.add_css_class(indicator_class)
        self.add_css_class(indicator_class)

    def _indicator_label(self, indicator_class: str) -> str:
        if indicator_class.endswith("green"):
            return "On track"
        if indicator_class.endswith("yellow"):
            return "Watch closely"
        return "Needs attention"


class StatsWindow(Adw.ApplicationWindow):
    """Statistics dashboard for day, week, and month summaries."""

    def __init__(
        self,
        app: Adw.Application,
        group_service: GroupService,
        stats_service: GroupStatsService | None = None,
        group_id: str | None = None,
    ) -> None:
        super().__init__(application=app)
        self.group_service = group_service
        self.stats_service = stats_service or GroupStatsService(  # type: ignore[no-untyped-call]
            group_service.db
        )
        self.group_id = group_id
        self.selected_period = "today"

        self.metric_cards: dict[str, MetricCard] = {}
        self.period_buttons: dict[str, Gtk.CheckButton] = {}
        self.chart_bars: list[tuple[Gtk.Label, Gtk.LevelBar, Gtk.Label]] = []

        self.set_title("Statistics")
        self.set_default_size(900, 700)
        self.add_css_class("stats-window")
        self._load_styles()

        self.set_content(self._build_content())
        self._refresh_stats()

    def _load_styles(self) -> None:
        """Load optional dashboard-specific CSS."""
        css_path = Path(__file__).with_name("styles_stats.css")
        if not css_path.exists() or css_path.stat().st_size == 0:
            return

        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_path))
        display = self.get_display() or Gdk.Display.get_default()
        if display is None:
            return
        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _build_content(self) -> Gtk.Widget:
        """Create the dashboard layout."""
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)

        header_label = Gtk.Label(label="Session Statistics")
        header_label.set_xalign(0.0)
        header_label.add_css_class("title-1")
        content.append(header_label)

        content.append(self._build_period_selector())
        content.append(self._build_metrics_grid())
        content.append(self._build_chart_section())
        content.append(self._build_footer())

        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(content)
        outer.append(scroll)
        return outer

    def _build_period_selector(self) -> Gtk.Box:
        """Build the period radio selector."""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        container.add_css_class("linked")

        first_button: Gtk.CheckButton | None = None
        for period_key in ("today", "week", "month"):
            button = Gtk.CheckButton(label=PERIOD_LABELS[period_key])
            button.set_can_focus(True)
            if first_button is None:
                first_button = button
            else:
                button.set_group(first_button)
            button.connect("toggled", self._on_period_selected, period_key)
            self.period_buttons[period_key] = button
            container.append(button)

        self.period_buttons["today"].set_active(True)
        return container

    def _build_metrics_grid(self) -> Gtk.FlowBox:
        """Build the responsive metric card grid."""
        self.metrics_flow = Gtk.FlowBox()
        self.metrics_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.metrics_flow.set_max_children_per_line(2)
        self.metrics_flow.set_min_children_per_line(1)
        self.metrics_flow.set_homogeneous(True)
        self.metrics_flow.set_column_spacing(12)
        self.metrics_flow.set_row_spacing(12)
        self.metrics_flow.set_hexpand(True)

        for key, title in (
            ("completion_rate", "Completion Rate"),
            ("expiration_rate", "Expiration Rate"),
            ("overtime_minutes", "Overtime"),
            ("pause_fragmentation", "Pause Fragmentation"),
            ("focus_consistency", "Focus Consistency"),
            ("total_focus_time", "Total Focus Time"),
        ):
            card = MetricCard(title)
            self.metric_cards[key] = card
            self.metrics_flow.insert(card, -1)

        return self.metrics_flow

    def _build_chart_section(self) -> Gtk.Box:
        """Build a lightweight activity chart section."""
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        wrapper.add_css_class("stats-chart")

        heading = Gtk.Label(label="Focus activity")
        heading.set_xalign(0.0)
        heading.add_css_class("title-4")
        wrapper.append(heading)

        subheading = Gtk.Label(
            label="Daily totals update with the selected period for quick trend scanning."
        )
        subheading.set_xalign(0.0)
        subheading.set_wrap(True)
        subheading.add_css_class("dim-label")
        wrapper.append(subheading)

        self.chart_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        wrapper.append(self.chart_box)
        return wrapper

    def _build_footer(self) -> Gtk.Box:
        """Build footer actions and last update timestamp."""
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        footer.set_halign(Gtk.Align.FILL)

        self.last_updated_label = Gtk.Label(label="Last updated: --:--")
        self.last_updated_label.set_xalign(0.0)
        self.last_updated_label.add_css_class("dim-label")
        self.last_updated_label.set_hexpand(True)
        footer.append(self.last_updated_label)

        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.set_can_focus(True)
        refresh_button.connect("clicked", self._on_refresh_clicked)
        footer.append(refresh_button)
        self.refresh_button = refresh_button
        return footer

    def _on_period_selected(
        self,
        button: Gtk.CheckButton,
        period_key: str,
    ) -> None:
        """Refresh the dashboard when the selected period changes."""
        if not button.get_active() or self.selected_period == period_key:
            return
        self.selected_period = period_key
        self._refresh_stats()

    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        """Handle manual refreshes."""
        self._refresh_stats()

    def _refresh_stats(self) -> None:
        """Load fresh data from the stats service and update the view."""
        dashboard = self._load_dashboard_data(self.selected_period)
        for key, card in self.metric_cards.items():
            card.update(dashboard.metrics[key])
        self._update_chart(dashboard.chart_rows)
        self.last_updated_label.set_label(
            f"Last updated: {datetime.now().strftime('%H:%M')}"
        )

    def _load_dashboard_data(self, period_key: str) -> DashboardData:
        """Collect metrics from the active stats service."""
        if hasattr(self.stats_service, "calculate_stats"):
            modern_dashboard = self._try_build_modern_dashboard(period_key)
            if modern_dashboard is not None:
                return modern_dashboard
        return self._build_legacy_dashboard(period_key)

    def _try_build_modern_dashboard(self, period_key: str) -> DashboardData | None:
        """Normalize dashboards returned by a richer stats service implementation."""
        calculate_stats = getattr(self.stats_service, "calculate_stats", None)
        if calculate_stats is None:
            return None

        try:
            raw_data = calculate_stats(self.group_id, period_key)
        except TypeError:
            try:
                raw_data = calculate_stats(period_key)
            except TypeError:
                return None

        if raw_data is None:
            return None

        metrics = {
            "completion_rate": self._metric_from_source(
                raw_data,
                "Completion Rate",
                field_name="completion_rate",
                detail_default="Tasks finished within the selected period.",
                value_formatter=self._format_percent,
                color_resolver=lambda value: self._color_for_higher(value, 80.0, 50.0),
                higher_is_better=True,
            ),
            "expiration_rate": self._metric_from_source(
                raw_data,
                "Expiration Rate",
                field_name="expiration_rate",
                detail_default="Tasks that ran out of time before completion.",
                value_formatter=self._format_percent,
                color_resolver=lambda value: self._color_for_lower(value, 10.0, 30.0),
                higher_is_better=False,
            ),
            "overtime_minutes": self._metric_from_source(
                raw_data,
                "Overtime",
                field_name="overtime_minutes",
                detail_default="Average minutes spent beyond the planned duration.",
                value_formatter=lambda value: self._format_number(value, 1),
                unit="min",
                color_resolver=lambda value: self._color_for_lower(value, 5.0, 15.0),
                higher_is_better=False,
            ),
            "pause_fragmentation": self._metric_from_source(
                raw_data,
                "Pause Fragmentation",
                field_name="pause_fragmentation",
                detail_default="0 means focused blocks, 1 means fragmented work.",
                value_formatter=lambda value: self._format_number(value, 2),
                color_resolver=lambda value: self._color_for_lower(value, 0.25, 0.5),
                higher_is_better=False,
            ),
            "focus_consistency": self._metric_from_source(
                raw_data,
                "Focus Consistency",
                field_name="focus_consistency",
                detail_default="Steady focus quality across the selected period.",
                value_formatter=self._format_percent,
                color_resolver=lambda value: self._color_for_higher(value, 70.0, 40.0),
                higher_is_better=True,
            ),
            "total_focus_time": self._metric_from_source(
                raw_data,
                "Total Focus Time",
                field_name="total_focus_time_seconds",
                detail_default="Time spent in focused execution for this period.",
                value_formatter=self._format_focus_time,
                color_resolver=lambda value: self._color_for_focus_time(value, period_key),
                higher_is_better=True,
            ),
        }

        chart_rows = self._chart_rows_from_source(raw_data)
        return DashboardData(metrics=metrics, chart_rows=chart_rows)

    def _metric_from_source(
        self,
        source: object,
        title: str,
        *,
        field_name: str,
        detail_default: str,
        value_formatter: Any,
        color_resolver: Any,
        higher_is_better: bool,
        unit: str = "",
    ) -> MetricData:
        """Build a metric card from dict-like or object-like data."""
        metric_source = self._lookup_value(source, field_name)
        raw_value = self._coerce_number(metric_source)
        detail = self._lookup_nested_text(metric_source, "detail", "subtitle") or detail_default
        metric_unit = self._lookup_nested_text(metric_source, "unit") or unit
        trend = self._extract_trend_text(metric_source, higher_is_better)
        return MetricData(
            title=title,
            value=value_formatter(raw_value),
            unit=metric_unit,
            detail=detail,
            indicator_class=color_resolver(raw_value),
            trend=trend,
        )

    def _extract_trend_text(self, metric_source: object, higher_is_better: bool) -> str:
        """Return trend text when the data source provides comparison data."""
        trend_value = self._lookup_nested_value(metric_source, "trend", "delta")
        if trend_value is None:
            previous_value = self._lookup_nested_value(metric_source, "previous")
            current_value = self._lookup_nested_value(metric_source, "value")
            if previous_value is None or current_value is None:
                return ""
            return self._format_trend(
                self._coerce_number(current_value),
                self._coerce_number(previous_value),
                period_key=self.selected_period,
                higher_is_better=higher_is_better,
                unit=self._lookup_nested_text(metric_source, "unit") or "",
            )

        delta = self._coerce_number(trend_value)
        baseline = PERIOD_COMPARISON_LABELS[self.selected_period]
        arrow = "↑" if (delta >= 0) == higher_is_better else "↓"
        return f"{arrow} {self._format_number(abs(delta), 1)} vs {baseline}"

    def _chart_rows_from_source(self, source: object) -> list[ChartRow]:
        """Extract optional chart rows from richer service payloads."""
        chart_source = self._lookup_value(source, "chart_rows")
        if not isinstance(chart_source, list):
            return []

        rows: list[ChartRow] = []
        for item in chart_source:
            label = self._lookup_nested_text(item, "label", "name")
            if label == "":
                continue
            raw_value = self._lookup_nested_value(item, "value", "seconds")
            value = int(round(self._coerce_number(raw_value)))
            rows.append(ChartRow(label=label, value_seconds=value))
        return rows

    def _build_legacy_dashboard(self, period_key: str) -> DashboardData:
        """Build the dashboard from the legacy period stats service."""
        days = PERIOD_DAYS[period_key]
        comparison_period = self.stats_service.get_period_stats(days * 2)
        current_daily = comparison_period.daily_stats[-days:]
        previous_daily = comparison_period.daily_stats[:-days]
        current = self._aggregate_daily_stats(current_daily)
        previous = self._aggregate_daily_stats(previous_daily)

        completion_rate = self._completion_rate(current)
        previous_completion_rate = self._completion_rate(previous)
        expiration_rate = max(0.0, 100.0 - completion_rate)
        previous_expiration_rate = max(0.0, 100.0 - previous_completion_rate)
        pause_fragmentation = self._pause_fragmentation(current)
        previous_pause_fragmentation = self._pause_fragmentation(previous)
        focus_consistency = completion_rate * (1.0 - pause_fragmentation)
        previous_focus_consistency = previous_completion_rate * (1.0 - previous_pause_fragmentation)
        overtime_minutes = self._overtime_minutes(current)
        previous_overtime_minutes = self._overtime_minutes(previous)

        metrics = {
            "completion_rate": MetricData(
                title="Completion Rate",
                value=self._format_percent(completion_rate),
                unit="",
                detail=f"{current.tasks_completed} tasks completed in this period",
                indicator_class=self._color_for_higher(completion_rate, 80.0, 50.0),
                trend=self._format_trend(
                    completion_rate,
                    previous_completion_rate,
                    period_key=period_key,
                    higher_is_better=True,
                ),
            ),
            "expiration_rate": MetricData(
                title="Expiration Rate",
                value=self._format_percent(expiration_rate),
                unit="",
                detail="Calculated from unfinished capacity in the selected period",
                indicator_class=self._color_for_lower(expiration_rate, 10.0, 30.0),
                trend=self._format_trend(
                    expiration_rate,
                    previous_expiration_rate,
                    period_key=period_key,
                    higher_is_better=False,
                ),
            ),
            "overtime_minutes": MetricData(
                title="Overtime",
                value=self._format_number(overtime_minutes, 1),
                unit="min",
                detail="Average extra minutes beyond the planned budget",
                indicator_class=self._color_for_lower(overtime_minutes, 5.0, 15.0),
                trend=self._format_trend(
                    overtime_minutes,
                    previous_overtime_minutes,
                    period_key=period_key,
                    higher_is_better=False,
                    unit=" min",
                ),
            ),
            "pause_fragmentation": MetricData(
                title="Pause Fragmentation",
                value=self._format_number(pause_fragmentation, 2),
                unit="score",
                detail=f"{current.interruptions} interruption events recorded",
                indicator_class=self._color_for_lower(pause_fragmentation, 0.25, 0.5),
                trend=self._format_trend(
                    pause_fragmentation,
                    previous_pause_fragmentation,
                    period_key=period_key,
                    higher_is_better=False,
                ),
            ),
            "focus_consistency": MetricData(
                title="Focus Consistency",
                value=self._format_percent(focus_consistency),
                unit="",
                detail="Completion quality adjusted by interruption pressure",
                indicator_class=self._color_for_higher(focus_consistency, 70.0, 40.0),
                trend=self._format_trend(
                    focus_consistency,
                    previous_focus_consistency,
                    period_key=period_key,
                    higher_is_better=True,
                ),
            ),
            "total_focus_time": MetricData(
                title="Total Focus Time",
                value=self._format_focus_time(float(current.total_focus_time_seconds)),
                unit="",
                detail=f"{current.groups_executed} groups executed",
                indicator_class=self._color_for_focus_time(
                    float(current.total_focus_time_seconds),
                    period_key,
                ),
                trend=self._format_trend(
                    float(current.total_focus_time_seconds),
                    float(previous.total_focus_time_seconds),
                    period_key=period_key,
                    higher_is_better=True,
                    unit="",
                    value_formatter=self._format_focus_time,
                ),
            ),
        }

        chart_rows = [
            ChartRow(label=entry.date[5:], value_seconds=entry.total_time_seconds)
            for entry in current_daily
        ]
        return DashboardData(metrics=metrics, chart_rows=chart_rows)

    def _aggregate_daily_stats(self, daily_stats: list[DailyGroupStats]) -> LegacyAggregate:
        """Aggregate daily stats from the legacy service."""
        return LegacyAggregate(
            groups_executed=sum(day.groups_executed for day in daily_stats),
            tasks_completed=sum(day.tasks_completed for day in daily_stats),
            total_focus_time_seconds=sum(day.total_time_seconds for day in daily_stats),
            interruptions=sum(day.interruptions for day in daily_stats),
        )

    def _completion_rate(self, aggregate: LegacyAggregate) -> float:
        """Estimate completion rate using legacy stats totals."""
        estimated_capacity = max(1, aggregate.total_focus_time_seconds // 600)
        return min(100.0, (aggregate.tasks_completed / estimated_capacity) * 100.0)

    def _pause_fragmentation(self, aggregate: LegacyAggregate) -> float:
        """Estimate pause fragmentation from interruption density."""
        total_activity = aggregate.tasks_completed + aggregate.interruptions
        if total_activity <= 0:
            return 0.0
        return min(1.0, aggregate.interruptions / total_activity)

    def _overtime_minutes(self, aggregate: LegacyAggregate) -> float:
        """Estimate overtime pressure from interruption-heavy sessions."""
        if aggregate.groups_executed <= 0:
            return 0.0
        overtime_seconds = max(0, aggregate.interruptions * 120)
        return overtime_seconds / 60.0 / aggregate.groups_executed

    def _format_trend(
        self,
        current_value: float,
        previous_value: float,
        *,
        period_key: str,
        higher_is_better: bool,
        unit: str = "",
        value_formatter: Any | None = None,
    ) -> str:
        """Create consistent trend text for metric cards."""
        if abs(current_value - previous_value) < 0.01:
            return ""

        improving = (
            current_value >= previous_value
            if higher_is_better
            else current_value <= previous_value
        )
        arrow = "↑" if improving else "↓"
        comparison_label = PERIOD_COMPARISON_LABELS[period_key]
        delta = abs(current_value - previous_value)

        if value_formatter is not None:
            formatted_delta = value_formatter(delta)
        elif unit:
            formatted_delta = f"{self._format_number(delta, 1)}{unit}"
        else:
            formatted_delta = self._format_number(delta, 1)
        return f"{arrow} {formatted_delta} vs {comparison_label}"

    def _update_chart(self, chart_rows: list[ChartRow]) -> None:
        """Refresh the small activity chart."""
        while (child := self.chart_box.get_first_child()) is not None:
            self.chart_box.remove(child)
        self.chart_bars.clear()

        if not chart_rows:
            empty = Gtk.Label(label="No activity recorded for this period yet.")
            empty.set_xalign(0.0)
            empty.add_css_class("dim-label")
            self.chart_box.append(empty)
            return

        max_value = max(row.value_seconds for row in chart_rows) or 1
        for row in chart_rows:
            line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

            label = Gtk.Label(label=row.label)
            label.set_xalign(0.0)
            label.set_size_request(72, -1)
            line.append(label)

            level = Gtk.LevelBar.new_for_interval(0.0, float(max_value))
            level.set_value(float(row.value_seconds))
            level.set_hexpand(True)
            line.append(level)

            value_label = Gtk.Label(label=self._format_focus_time(float(row.value_seconds)))
            value_label.set_xalign(1.0)
            line.append(value_label)

            self.chart_box.append(line)
            self.chart_bars.append((label, level, value_label))

    def _lookup_value(self, source: object, field_name: str) -> object:
        """Read a value from a dict-like or object-like source."""
        if isinstance(source, dict):
            return source.get(field_name)
        return getattr(source, field_name, None)

    def _lookup_nested_value(self, source: object, *field_names: str) -> object | None:
        """Read nested values from dict-like or object-like sources."""
        for field_name in field_names:
            value = self._lookup_value(source, field_name)
            if value is not None:
                return value
        return None

    def _lookup_nested_text(self, source: object, *field_names: str) -> str:
        """Return a text field when available."""
        value = self._lookup_nested_value(source, *field_names)
        if isinstance(value, str):
            return value
        return ""

    def _coerce_number(self, value: object) -> float:
        """Coerce numeric-looking values to floats."""
        if isinstance(value, dict):
            nested_value = value.get("value")
            return self._coerce_number(nested_value)
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0

    def _format_percent(self, value: float) -> str:
        """Format a percentage without trailing decimals for whole numbers."""
        if value.is_integer():
            return f"{int(value)}%"
        return f"{value:.1f}%"

    def _format_number(self, value: float, decimals: int) -> str:
        """Format a number with optional trimming."""
        formatted = f"{value:.{decimals}f}"
        return formatted.rstrip("0").rstrip(".")

    def _format_focus_time(self, value_seconds: float) -> str:
        """Format focus time as hours and minutes."""
        total_seconds = max(0, int(round(value_seconds)))
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes:02d}m"

    def _color_for_higher(
        self,
        value: float,
        green_threshold: float,
        yellow_threshold: float,
    ) -> str:
        """Return a status class when higher values are better."""
        if value >= green_threshold:
            return "stats-indicator-green"
        if value >= yellow_threshold:
            return "stats-indicator-yellow"
        return "stats-indicator-red"

    def _color_for_lower(
        self,
        value: float,
        green_threshold: float,
        yellow_threshold: float,
    ) -> str:
        """Return a status class when lower values are better."""
        if value <= green_threshold:
            return "stats-indicator-green"
        if value <= yellow_threshold:
            return "stats-indicator-yellow"
        return "stats-indicator-red"

    def _color_for_focus_time(self, value_seconds: float, period_key: str) -> str:
        """Return a status class for total focus time based on the active period."""
        hours = value_seconds / 3600.0
        thresholds = {
            "today": (4.0, 2.0),
            "week": (20.0, 10.0),
            "month": (80.0, 40.0),
        }
        green_threshold, yellow_threshold = thresholds[period_key]
        return self._color_for_higher(hours, green_threshold, yellow_threshold)
