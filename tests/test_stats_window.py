"""Tests for the statistics dashboard window."""

from __future__ import annotations

from dataclasses import dataclass

import gi  # type: ignore[import-untyped]
import pytest

from pulse_task.core.group_service import GroupService
from pulse_task.core.persistence import Database
from pulse_task.core.stats import DailyGroupStats, PeriodGroupStats
from pulse_task.ui.stats_window import StatsWindow

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw  # type: ignore[import-untyped]  # noqa: E402


@dataclass
class FakeModernStatsService:
    """Simple stats service that exposes the new calculate_stats API."""

    calls: list[tuple[str | None, str]]

    def calculate_stats(self, group_id: str | None, period: str) -> dict[str, object]:
        self.calls.append((group_id, period))
        if period == "week":
            completion_value = 92.0
            total_focus_time = 43200
        else:
            completion_value = 85.0
            total_focus_time = 14400

        return {
            "completion_rate": {
                "value": completion_value,
                "detail": "17 of 20 tasks",
                "trend": 5.0,
            },
            "expiration_rate": {
                "value": 10.0,
                "detail": "2 expired tasks",
                "trend": -2.0,
            },
            "overtime_minutes": {
                "value": 4.5,
                "detail": "Small overtime",
                "trend": -1.5,
                "unit": "min",
            },
            "pause_fragmentation": {
                "value": 0.2,
                "detail": "Low fragmentation",
                "trend": -0.1,
            },
            "focus_consistency": {
                "value": 78.0,
                "detail": "Stable focus",
                "trend": 4.0,
            },
            "total_focus_time_seconds": {
                "value": total_focus_time,
                "detail": "4 focused sessions",
            },
            "chart_rows": [
                {"label": "Mon", "value": 3600},
                {"label": "Tue", "value": 5400},
            ],
        }


class FakeLegacyStatsService:
    """Fallback stats service that only exposes get_period_stats."""

    def get_period_stats(self, days: int) -> PeriodGroupStats:
        daily_stats = [
            DailyGroupStats(
                date=f"2024-01-{day:02d}",
                groups_executed=1,
                tasks_completed=2 if day < days else 3,
                total_time_seconds=1800 if day < days else 3600,
                interruptions=0 if day < days else 1,
            )
            for day in range(1, days + 1)
        ]
        return PeriodGroupStats(
            period_days=days,
            start_date="2024-01-01",
            end_date="2024-01-31",
            groups_executed=sum(day.groups_executed for day in daily_stats),
            tasks_completed=sum(day.tasks_completed for day in daily_stats),
            total_focus_time_seconds=sum(day.total_time_seconds for day in daily_stats),
            avg_group_duration_seconds=1800,
            completion_rate=50.0,
            interruption_rate=0.5,
            daily_stats=daily_stats,
        )


@pytest.fixture(scope="session")
def adw_app() -> Adw.Application:
    """Create a minimal Adwaita application for window tests."""
    app = Adw.Application(application_id="com.example.pulsetasktests")
    app.register()
    return app


@pytest.fixture
def group_service() -> GroupService:
    """Create an in-memory group service."""
    return GroupService(Database(":memory:"))


def test_stats_window_renders_all_metric_cards(
    adw_app: Adw.Application,
    group_service: GroupService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The window should create and populate all six metric cards."""
    monkeypatch.setattr(StatsWindow, "_load_styles", lambda self: None)
    stats_service = FakeModernStatsService(calls=[])

    window = StatsWindow(adw_app, group_service, stats_service)

    assert window.get_title() == "Statistics"
    assert len(window.metric_cards) == 6
    assert stats_service.calls == [(None, "today")]
    assert window.metric_cards["completion_rate"].value_label.get_label() == "85%"
    assert window.metric_cards["completion_rate"].detail_label.get_label() == "17 of 20 tasks"
    assert "stats-indicator-green" in window.metric_cards["completion_rate"].get_css_classes()
    assert len(window.chart_bars) == 2


def test_period_selector_refreshes_dashboard(
    adw_app: Adw.Application,
    group_service: GroupService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Selecting a new period should recalculate the dashboard."""
    monkeypatch.setattr(StatsWindow, "_load_styles", lambda self: None)
    stats_service = FakeModernStatsService(calls=[])
    window = StatsWindow(adw_app, group_service, stats_service)

    window.period_buttons["week"].set_active(True)

    assert window.selected_period == "week"
    assert stats_service.calls[-1] == (None, "week")
    assert window.metric_cards["completion_rate"].value_label.get_label() == "92%"
    assert window.metric_cards["total_focus_time"].value_label.get_label() == "12h 00m"


def test_stats_window_supports_legacy_group_stats_service(
    adw_app: Adw.Application,
    group_service: GroupService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The dashboard should gracefully fall back to the legacy stats API."""
    monkeypatch.setattr(StatsWindow, "_load_styles", lambda self: None)

    window = StatsWindow(adw_app, group_service, FakeLegacyStatsService())

    assert window.metric_cards["completion_rate"].value_label.get_label() == "50%"
    assert window.metric_cards["pause_fragmentation"].value_label.get_label() == "0.25"
    assert window.metric_cards["total_focus_time"].value_label.get_label() == "1h 00m"
    assert len(window.chart_bars) == 1
