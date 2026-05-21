from pulse_task.core.stats import build_productivity_stats, format_productivity_report


def test_build_productivity_stats_rates() -> None:
    stats = build_productivity_stats(
        {
            "tasks_started": 10,
            "tasks_completed": 7,
            "tasks_expired": 2,
            "tasks_paused": 4,
            "tasks_resumed": 3,
            "tasks_snoozed": 1,
            "tasks_recovered": 2,
        }
    )

    assert stats.tasks_started == 10
    assert stats.tasks_completed == 7
    assert stats.tasks_expired == 2
    assert stats.tasks_paused == 4
    assert stats.tasks_resumed == 3
    assert stats.tasks_snoozed == 1
    assert stats.tasks_recovered == 2
    assert stats.completion_rate_pct == 70.0
    assert stats.expiration_rate_pct == 20.0
    assert stats.resume_after_pause_pct == 75.0


def test_build_productivity_stats_handles_zero_denominators() -> None:
    stats = build_productivity_stats({})

    assert stats.completion_rate_pct == 0.0
    assert stats.expiration_rate_pct == 0.0
    assert stats.resume_after_pause_pct == 0.0


def test_format_productivity_report_contains_key_lines() -> None:
    stats = build_productivity_stats(
        {
            "tasks_started": 5,
            "tasks_completed": 3,
            "tasks_expired": 1,
            "tasks_paused": 2,
            "tasks_resumed": 1,
        }
    )

    report = format_productivity_report(stats)

    assert "PulseTask local metrics report" in report
    assert "Tasks started: 5" in report
    assert "Completion rate: 60.00%" in report
