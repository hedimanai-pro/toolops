"""
Name: observability.py

Description: Metrics and observability bridge for ToolOps SDK.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from contextlib import nullcontext
from collections import defaultdict


DEFAULT_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)


def _label_key(labels: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """
    Convert labels dictionary to a sorted tuple key.

    Args:
        labels: Dictionary of label names and values.

    Returns:
        Sorted tuple of label pairs.
    """

    return tuple(sorted((name, str(value)) for name, value in labels.items()))


def _render_labels(labels: tuple[tuple[str, str], ...]) -> str:
    """
    Render label tuples into Prometheus format string.

    Args:
        labels: Tuple of label pairs.

    Returns:
        Prometheus formatted label string.
    """

    if not labels:
        return ""

    parts = [f'{name}="{value}"' for name, value in labels]
    return "{" + ",".join(parts) + "}"


@dataclass(slots=True)
class HistogramSnapshot:
    """Data class representing a histogram snapshot."""

    count: int = 0
    total: float = 0.0
    buckets: dict[float, int] | None = None


class PrometheusMetrics:
    """Internal Prometheus metrics registry and renderer."""


    def __init__(self) -> None:
        """Initialize the metrics registry."""

        self._counters: dict[str, dict[tuple[tuple[str, str], ...], float]] = defaultdict(dict)
        self._gauges: dict[str, dict[tuple[tuple[str, str], ...], float]] = defaultdict(dict)
        self._histograms: dict[str, dict[tuple[tuple[str, str], ...], HistogramSnapshot]] = defaultdict(dict)
        self._metadata: dict[str, tuple[str, str]] = {}


    def reset(self) -> None:
        """Reset all stored metrics and metadata."""

        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._metadata.clear()


    def counter(self, name: str, description: str, *, value: float = 1.0, labels: dict[str, Any] | None = None) -> None:
        """
        Increment a counter metric.

        Args:
            name: Metric name.
            description: Metric description.
            value: Increment value.
            labels: Optional labels.
        """

        label_key = _label_key(labels or {})
        self._metadata[name] = ("counter", description)
        series = self._counters[name]
        series[label_key] = series.get(label_key, 0.0) + value


    def gauge(self, name: str, description: str, *, value: float, labels: dict[str, Any] | None = None) -> None:
        """
        Set a gauge metric value.

        Args:
            name: Metric name.
            description: Metric description.
            value: Metric value.
            labels: Optional labels.
        """

        label_key = _label_key(labels or {})
        self._metadata[name] = ("gauge", description)
        self._gauges[name][label_key] = value


    def histogram(self, name: str, description: str, *, value: float, labels: dict[str, Any] | None = None, buckets: tuple[float, ...] = DEFAULT_BUCKETS) -> None:
        """
        Observe a value in a histogram.

        Args:
            name: Metric name.
            description: Metric description.
            value: Observed value.
            labels: Optional labels.
            buckets: Histogram buckets.
        """

        label_key = _label_key(labels or {})
        self._metadata[name] = ("histogram", description)
        series = self._histograms[name]
        snapshot = series.get(label_key)
        if snapshot is None:
            snapshot = HistogramSnapshot(buckets={bucket: 0 for bucket in buckets})
            series[label_key] = snapshot

        snapshot.count += 1
        snapshot.total += value
        assert snapshot.buckets is not None
        for bucket in buckets:
            if value <= bucket:
                snapshot.buckets[bucket] += 1


    def render(self) -> str:
        """
        Render metrics in Prometheus text format.

        Returns:
            Formatted metrics string.
        """

        lines: list[str] = []

        for name, series in sorted(self._counters.items()):
            metric_type, description = self._metadata[name]
            lines.append(f"# HELP {name} {description}")
            lines.append(f"# TYPE {name} {metric_type}")
            for labels, value in sorted(series.items()):
                lines.append(f"{name}{_render_labels(labels)} {value}")

        for name, series in sorted(self._gauges.items()):
            metric_type, description = self._metadata[name]
            lines.append(f"# HELP {name} {description}")
            lines.append(f"# TYPE {name} {metric_type}")
            for labels, value in sorted(series.items()):
                lines.append(f"{name}{_render_labels(labels)} {value}")

        for name, series in sorted(self._histograms.items()):
            metric_type, description = self._metadata[name]
            lines.append(f"# HELP {name} {description}")
            lines.append(f"# TYPE {name} {metric_type}")
            for labels, snapshot in sorted(series.items()):
                assert snapshot.buckets is not None
                cumulative = 0
                for bucket, count in sorted(snapshot.buckets.items()):
                    cumulative += count
                    bucket_labels = labels + (("le", str(bucket)),)
                    lines.append(f"{name}_bucket{_render_labels(bucket_labels)} {cumulative}")

                inf_labels = labels + (("le", "+Inf"),)
                lines.append(f"{name}_bucket{_render_labels(inf_labels)} {snapshot.count}")
                lines.append(f"{name}_count{_render_labels(labels)} {snapshot.count}")
                lines.append(f"{name}_sum{_render_labels(labels)} {snapshot.total}")

        return "\n".join(lines) + ("\n" if lines else "")


class OpenTelemetryBridge:
    """Bridge for OpenTelemetry tracing support."""


    def __init__(self) -> None:
        """Initialize the OpenTelemetry bridge."""

        self._tracer: Any = None


    def configure(self, tracer: Any | None = None) -> None:
        """
        Configure the OpenTelemetry tracer.

        Args:
            tracer: Optional tracer instance.
        """

        if tracer is not None:
            self._tracer = tracer
            return

        try:
            from opentelemetry import trace  # type: ignore[import]
            self._tracer = trace.get_tracer("toolops")

        except ImportError:
            self._tracer = None


    def start_span(self, name: str, *, attributes: dict[str, Any] | None = None) -> Any:
        """
        Start a new OpenTelemetry span.

        Args:
            name: Span name.
            attributes: Optional span attributes.

        Returns:
            Span context manager.
        """

        if self._tracer is None:
            return nullcontext(None)
        return _SpanContext(self._tracer, name, attributes or {})


class _SpanContext:
    """Context manager for OpenTelemetry spans."""


    def __init__(self, tracer: Any, name: str, attributes: dict[str, Any]) -> None:
        """
        Initialize the span context.

        Args:
            tracer: Tracer instance.
            name: Span name.
            attributes: Span attributes.
        """

        self._context = tracer.start_as_current_span(name)
        self._attributes = attributes
        self._span: Any = None


    def __enter__(self) -> Any:
        """
        Enter the span context.

        Returns:
            The active span.
        """

        self._span = self._context.__enter__()
        if self._span is not None:
            for name, value in self._attributes.items():
                self._span.set_attribute(name, value)

        return self._span


    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        """
        Exit the span context.

        Args:
            exc_type: Exception type.
            exc: Exception instance.
            tb: Traceback.

        Returns:
            Boolean indicating if exception was handled.
        """

        return self._context.__exit__(exc_type, exc, tb)


class ToolOpsMetrics:
    """Central coordinator for ToolOps observability."""


    def __init__(self) -> None:
        """Initialize ToolOps metrics and tracing bridge."""

        self._prometheus = PrometheusMetrics()
        self._otel = OpenTelemetryBridge()


    @property
    def otel(self) -> OpenTelemetryBridge:
        """Access the OpenTelemetry bridge."""

        return self._otel


    def configure_opentelemetry(self, tracer: Any | None = None) -> None:
        """
        Configure tracing via OpenTelemetry.

        Args:
            tracer: Optional tracer instance.
        """

        self._otel.configure(tracer)


    def record_tool_start(self, *, tool: str, cache: str | None) -> None:
        """
        Record the start of a tool call.

        Args:
            tool: Tool name.
            cache: Cache name or None.
        """

        self._prometheus.counter(
            "toolops_tool_calls_total",
            "Total ToolOps tool invocations by status.",
            labels={"tool": tool, "status": "started", "cache": cache or "none"},
        )


    def record_tool_result(self, *, tool: str, status: str, duration_s: float, cache: str | None, cached: bool) -> None:
        """
        Record the result of a tool call.

        Args:
            tool: Tool name.
            status: Call status.
            duration_s: Execution duration.
            cache: Cache name or None.
            cached: Whether result was from cache.
        """

        base_labels = {
            "tool": tool,
            "status": status,
            "cache": cache or "none",
            "cached": str(cached).lower(),
        }

        self._prometheus.counter(
            "toolops_tool_calls_total",
            "Total ToolOps tool invocations by status.",
            labels=base_labels,
        )

        self._prometheus.histogram(
            "toolops_tool_duration_seconds",
            "Tool execution duration in seconds.",
            value=duration_s,
            labels={
                "tool": tool,
                "status": status,
                "cache": cache or "none",
            },
        )


    def record_cache_hit(self, *, tool: str, cache: str, hit_kind: str = "fresh") -> None:
        """
        Record a cache hit.

        Args:
            tool: Tool name.
            cache: Cache name.
            hit_kind: Hit type (fresh/stale).
        """

        self._prometheus.counter(
            "toolops_cache_hits_total",
            "Total ToolOps cache hits.",
            labels={"tool": tool, "cache": cache, "kind": hit_kind},
        )


    def record_retry(self, *, tool: str) -> None:
        """
        Record a tool execution retry.

        Args:
            tool: Tool name.
        """

        self._prometheus.counter(
            "toolops_retries_total",
            "Total ToolOps retries.",
            labels={"tool": tool},
        )


    def record_invalidation(self, *, cache: str, count: int) -> None:
        """
        Record cache entry invalidations.

        Args:
            cache: Cache name.
            count: Number of entries invalidated.
        """

        self._prometheus.counter(
            "toolops_cache_invalidations_total",
            "Total invalidated cache entries.",
            value=float(count),
            labels={"cache": cache},
        )


    def record_circuit_state(self, *, tool: str, state: str) -> None:
        """
        Record circuit breaker state changes.

        Args:
            tool: Tool name.
            state: New circuit state.
        """

        for name, value in {
            "closed": 1.0 if state == "closed" else 0.0,
            "open": 1.0 if state == "open" else 0.0,
            "half_open": 1.0 if state == "half_open" else 0.0,
        }.items():
            self._prometheus.gauge(
                "toolops_circuit_state",
                "Circuit breaker state by tool.",
                value=value,
                labels={"tool": tool, "state": name},
            )


    def render_prometheus(self) -> str:
        """
        Render all metrics in Prometheus format.

        Returns:
            Formatted metrics string.
        """

        return self._prometheus.render()


    def reset(self) -> None:
        """Reset all ToolOps metrics."""

        self._prometheus.reset()


metrics = ToolOpsMetrics()


def configure_opentelemetry(tracer: Any | None = None) -> None:
    """
    Global configuration for OpenTelemetry tracing.

    Args:
        tracer: Optional tracer instance.
    """

    metrics.configure_opentelemetry(tracer)


def prometheus_metrics() -> str:
    """
    Get all ToolOps metrics in Prometheus format.

    Returns:
        Formatted metrics string.
    """

    return metrics.render_prometheus()
