from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


class MetricsSink(Protocol):
    def increment(self, metric_name: str, amount: int = 1) -> None:
        ...


class NoOpMetrics:
    def increment(self, metric_name: str, amount: int = 1) -> None:
        _ = (metric_name, amount)


class LocalMetrics:
    """Persists lightweight local counters for task lifecycle observability."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._counters: dict[str, int] = {}
        self._load_from_disk()

    def increment(self, metric_name: str, amount: int = 1) -> None:
        if amount <= 0:
            return
        self._counters[metric_name] = self._counters.get(metric_name, 0) + amount
        self._persist_to_disk()

    def snapshot(self) -> dict[str, int]:
        return dict(self._counters)

    def _load_from_disk(self) -> None:
        if not self.file_path.exists():
            return
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        counters = raw.get("counters")
        if not isinstance(counters, dict):
            return

        loaded: dict[str, int] = {}
        for key, value in counters.items():
            if isinstance(key, str) and isinstance(value, int) and value >= 0:
                loaded[key] = value
        self._counters = loaded

    def _persist_to_disk(self) -> None:
        payload = {
            "updated_at": datetime.now(UTC).isoformat(),
            "counters": self._counters,
        }
        tmp_path = self.file_path.with_suffix(f"{self.file_path.suffix}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            tmp_path.replace(self.file_path)
        except OSError:
            return
