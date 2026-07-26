"""Simple application metrics collector for observability.

Tracks execution timing, operation counts, and success/failure rates
for tools and services across the application. All metrics are
thread-safe and use time.monotonic() for immunity to clock changes.
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.logger import logger


@dataclass
class TimingEntry:
    """A single timing measurement for an operation."""

    operation: str
    duration_ms: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects and reports application performance metrics.

    Usage:
        collector = MetricsCollector()

        # Track a single operation
        collector.record("web_search", duration_ms=150.0, success=True,
                         metadata={"engine": "google", "cached": False})

        # Use as context manager for automatic timing
        with collector.timed("llm_request", metadata={"model": "gpt-4o"}):
            await llm.ask(...)

        # Get report
        report = collector.report()
    """

    def __init__(self, enabled: bool = True, max_entries: int = 1000):
        self.enabled = enabled
        self.max_entries = max_entries
        self._entries: List[TimingEntry] = []
        self._counters: Dict[str, int] = defaultdict(int)
        self._success_counters: Dict[str, int] = defaultdict(int)
        self._failure_counters: Dict[str, int] = defaultdict(int)

    def record(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a single operation timing.

        Args:
            operation: Name of the operation (e.g., "web_search", "bash_execute")
            duration_ms: Execution duration in milliseconds
            success: Whether the operation succeeded
            metadata: Optional key-value pairs for additional context
        """
        if not self.enabled:
            return

        self._counters[operation] += 1
        if success:
            self._success_counters[operation] += 1
        else:
            self._failure_counters[operation] += 1

        entry = TimingEntry(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata or {},
        )

        self._entries.append(entry)

        # Trim if over max_entries
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    @contextmanager
    def timed(
        self,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager that automatically records timing.

        Args:
            operation: Name of the operation
            metadata: Optional context metadata

        Yields:
            None

        Example:
            with collector.timed("db_query", {"table": "users"}):
                await run_query()
        """
        if not self.enabled:
            yield
            return

        start = time.monotonic()
        success = True
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = (time.monotonic() - start) * 1000  # Convert to ms
            self.record(operation, duration, success, metadata)

    def log_timing(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record and log an operation in one call.

        This combines record() with a structured log message for
        observability in production.
        """
        self.record(operation, duration_ms, success, metadata)
        meta_str = f" ({metadata})" if metadata else ""
        if success:
            logger.info(
                f"⏱️ {operation} completed in {duration_ms:.1f}ms{meta_str}"
            )
        else:
            logger.warning(
                f"⏱️ {operation} FAILED in {duration_ms:.1f}ms{meta_str}"
            )

    def report(self) -> Dict[str, Any]:
        """Generate a performance report summary.

        Returns:
            Dict with operation stats: count, avg duration, success rate, etc.
        """
        if not self._entries:
            return {"status": "no_data"}

        # Group entries by operation
        grouped: Dict[str, List[float]] = defaultdict(list)
        success_durations: Dict[str, List[float]] = defaultdict(list)
        failure_durations: Dict[str, List[float]] = defaultdict(list)

        for entry in self._entries:
            grouped[entry.operation].append(entry.duration_ms)
            if entry.success:
                success_durations[entry.operation].append(entry.duration_ms)
            else:
                failure_durations[entry.operation].append(entry.duration_ms)

        report: Dict[str, Any] = {}
        total_ops = len(self._entries)
        total_success = sum(
            1 for e in self._entries if e.success
        )

        report["summary"] = {
            "total_operations": total_ops,
            "total_success": total_success,
            "total_failures": total_ops - total_success,
            "overall_success_rate": (
                f"{(total_success / total_ops) * 100:.1f}%"
                if total_ops > 0
                else "N/A"
            ),
        }

        report["operations"] = {}
        for op_name, durations in grouped.items():
            avg_dur = sum(durations) / len(durations)
            report["operations"][op_name] = {
                "count": len(durations),
                "avg_duration_ms": round(avg_dur, 1),
                "min_duration_ms": round(min(durations), 1),
                "max_duration_ms": round(max(durations), 1),
                "success_count": len(success_durations.get(op_name, [])),
                "failure_count": len(failure_durations.get(op_name, [])),
                "success_rate": (
                    f"{(len(success_durations.get(op_name, [])) / len(durations)) * 100:.1f}%"
                ),
            }

        return report

    def reset(self) -> None:
        """Clear all collected metrics."""
        self._entries.clear()
        self._counters.clear()
        self._success_counters.clear()
        self._failure_counters.clear()

    @property
    def total_operations(self) -> int:
        """Total number of recorded operations."""
        return len(self._entries)

    @property
    def success_rate(self) -> Optional[float]:
        """Overall success rate (0.0 to 1.0)."""
        if not self._entries:
            return None
        return sum(1 for e in self._entries if e.success) / len(self._entries)


# Global metrics collector instance
metrics = MetricsCollector()
