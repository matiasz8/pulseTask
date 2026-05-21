from __future__ import annotations

from pathlib import Path

from pulse_task.core.metrics import LocalMetrics
from pulse_task.core.stats import build_productivity_stats, format_productivity_report


def main() -> int:
    metrics_path = Path.home() / ".local" / "share" / "pulsetask" / "metrics.json"
    metrics = LocalMetrics(metrics_path)
    stats = build_productivity_stats(metrics.snapshot())
    print(format_productivity_report(stats))
    return 0
