from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 2)


@dataclass(slots=True)
class ProductivityStats:
    tasks_started: int
    tasks_completed: int
    tasks_expired: int
    tasks_paused: int
    tasks_resumed: int
    tasks_snoozed: int
    tasks_recovered: int
    completion_rate_pct: float
    expiration_rate_pct: float
    resume_after_pause_pct: float


def build_productivity_stats(counters: Mapping[str, int]) -> ProductivityStats:
    started = counters.get("tasks_started", 0)
    completed = counters.get("tasks_completed", 0)
    expired = counters.get("tasks_expired", 0)
    paused = counters.get("tasks_paused", 0)
    resumed = counters.get("tasks_resumed", 0)
    snoozed = counters.get("tasks_snoozed", 0)
    recovered = counters.get("tasks_recovered", 0)

    return ProductivityStats(
        tasks_started=started,
        tasks_completed=completed,
        tasks_expired=expired,
        tasks_paused=paused,
        tasks_resumed=resumed,
        tasks_snoozed=snoozed,
        tasks_recovered=recovered,
        completion_rate_pct=_ratio(completed, started),
        expiration_rate_pct=_ratio(expired, started),
        resume_after_pause_pct=_ratio(resumed, paused),
    )


def format_productivity_report(stats: ProductivityStats) -> str:
    return "\n".join(
        [
            "PulseTask local metrics report",
            "",
            f"Tasks started: {stats.tasks_started}",
            f"Tasks completed: {stats.tasks_completed}",
            f"Tasks expired: {stats.tasks_expired}",
            f"Tasks paused: {stats.tasks_paused}",
            f"Tasks resumed: {stats.tasks_resumed}",
            f"Tasks snoozed: {stats.tasks_snoozed}",
            f"Tasks recovered after restart: {stats.tasks_recovered}",
            "",
            f"Completion rate: {stats.completion_rate_pct:.2f}%",
            f"Expiration rate: {stats.expiration_rate_pct:.2f}%",
            f"Resume-after-pause rate: {stats.resume_after_pause_pct:.2f}%",
        ]
    )


# Group Execution Statistics

@dataclass(slots=True)
class DailyGroupStats:
    """Daily statistics for group execution."""

    date: str
    groups_executed: int
    tasks_completed: int
    total_time_seconds: int
    interruptions: int


@dataclass(slots=True)
class PeriodGroupStats:
    """Statistics for a period of group executions."""

    period_days: int
    start_date: str
    end_date: str
    groups_executed: int
    tasks_completed: int
    total_focus_time_seconds: int
    avg_group_duration_seconds: int
    completion_rate: float
    interruption_rate: float
    daily_stats: list[DailyGroupStats]


class GroupStatsService:
    """Compute statistics on group execution."""

    def __init__(self, db):  # type: ignore[no-untyped-def]
        """Initialize group stats service."""
        self.db = db

    def get_daily_stats(self, date: str) -> DailyGroupStats:
        """Get statistics for a specific date."""
        # Groups completed on this day
        query = (
            "SELECT COUNT(*), SUM(tasks_completed), "
            "SUM(total_time_seconds) "
            "FROM task_groups "
            "WHERE status = 'completed' AND DATE(completed_at) = ?"
        )
        result = self.db.fetch_one(query, (date,))

        groups = int(result[0]) if result and result[0] else 0
        tasks = int(result[1]) if result and result[1] else 0
        total_time = int(result[2]) if result and result[2] else 0

        # Interruptions = pauses + skips
        skip_query = (
            "SELECT SUM(tasks_skipped) FROM task_groups "
            "WHERE DATE(completed_at) = ?"
        )
        skip_result = self.db.fetch_one(skip_query, (date,))
        interruptions = int(skip_result[0]) if skip_result and skip_result[0] else 0

        return DailyGroupStats(
            date=date,
            groups_executed=groups,
            tasks_completed=tasks,
            total_time_seconds=total_time,
            interruptions=interruptions,
        )

    def get_period_stats(self, days: int = 7) -> PeriodGroupStats:
        """Get statistics for the last N days."""
        end_date = datetime.now(UTC).date()
        start_date = end_date - timedelta(days=days - 1)

        daily_stats = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            daily_stats.append(self.get_daily_stats(current_date.isoformat()))

        # Aggregate
        total_groups = sum(d.groups_executed for d in daily_stats)
        total_tasks = sum(d.tasks_completed for d in daily_stats)
        total_time = sum(d.total_time_seconds for d in daily_stats)
        total_interruptions = sum(d.interruptions for d in daily_stats)

        avg_duration = total_time // total_groups if total_groups > 0 else 0

        # Completion rate: actual tasks / potential (1 every 10min)
        estimated = total_time // 600 if total_time > 0 else 1
        completion_rate = min(1.0, max(0.0, total_tasks / estimated))

        interruption_rate = (
            total_interruptions / total_groups if total_groups > 0 else 0.0
        )

        return PeriodGroupStats(
            period_days=days,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            groups_executed=total_groups,
            tasks_completed=total_tasks,
            total_focus_time_seconds=total_time,
            avg_group_duration_seconds=avg_duration,
            completion_rate=completion_rate,
            interruption_rate=interruption_rate,
            daily_stats=daily_stats,
        )

    def export_csv(self, days: int = 30) -> str:
        """Export statistics as CSV."""
        period = self.get_period_stats(days)

        lines = [
            "date,groups_executed,tasks_completed,total_time_minutes,interruptions"
        ]

        for daily in period.daily_stats:
            minutes = daily.total_time_seconds // 60
            lines.append(
                f"{daily.date},{daily.groups_executed},"
                f"{daily.tasks_completed},{minutes},{daily.interruptions}"
            )

        lines.append("")
        lines.append("# Summary")
        lines.append(f"period_days,{period.period_days}")
        lines.append(f"groups_executed,{period.groups_executed}")
        lines.append(f"tasks_completed,{period.tasks_completed}")
        minutes = period.total_focus_time_seconds // 60
        lines.append(f"total_focus_time_minutes,{minutes}")
        lines.append(
            f"avg_group_duration_minutes,{period.avg_group_duration_seconds // 60}"
        )
        lines.append(f"completion_rate,{period.completion_rate:.2%}")
        lines.append(f"interruption_rate,{period.interruption_rate:.2f}")

        return "\n".join(lines)

    def export_json(self, days: int = 30) -> str:
        """Export statistics as JSON."""
        period = self.get_period_stats(days)

        data = {
            "period_days": period.period_days,
            "start_date": period.start_date,
            "end_date": period.end_date,
            "groups_executed": period.groups_executed,
            "tasks_completed": period.tasks_completed,
            "total_focus_time_seconds": period.total_focus_time_seconds,
            "avg_group_duration_seconds": period.avg_group_duration_seconds,
            "completion_rate": period.completion_rate,
            "interruption_rate": period.interruption_rate,
            "daily": [
                {
                    "date": d.date,
                    "groups_executed": d.groups_executed,
                    "tasks_completed": d.tasks_completed,
                    "total_time_seconds": d.total_time_seconds,
                    "interruptions": d.interruptions,
                }
                for d in period.daily_stats
            ],
        }

        return json.dumps(data, indent=2)

    def get_focus_heatmap(self, days: int = 7) -> dict[str, float]:
        """Get heatmap of focus by weekday."""
        end_date = datetime.now(UTC).date()
        start_date = end_date - timedelta(days=days - 1)

        weekday_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday_totals = {name: 0 for name in weekday_names}

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            weekday_name = weekday_names[current_date.weekday()]

            query = (
                "SELECT SUM(total_time_seconds) FROM task_groups "
                "WHERE DATE(completed_at) = ?"
            )
            result = self.db.fetch_one(query, (current_date.isoformat(),))
            if result and result[0]:
                weekday_totals[weekday_name] += int(result[0])

        # Normalize to 0.0-1.0
        max_time = max(weekday_totals.values()) if weekday_totals.values() else 1
        if max_time == 0:
            max_time = 1

        return {day: min(1.0, total / max_time) for day, total in weekday_totals.items()}
