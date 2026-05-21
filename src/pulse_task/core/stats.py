from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


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
