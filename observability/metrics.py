from __future__ import annotations

import threading
from collections import defaultdict


class MetricsRegistry:
    """
    Lightweight in-process metrics store.
    Good enough for logs/debugging and can later be replaced with Prometheus/OpenTelemetry.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._timings[name].append(value)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timings": {
                    k: {
                        "count": len(v),
                        "avg_ms": (sum(v) / len(v)) if v else 0.0,
                        "max_ms": max(v) if v else 0.0,
                    }
                    for k, v in self._timings.items()
                },
            }


metrics_registry = MetricsRegistry()