from __future__ import annotations

import os
import threading
from dataclasses import dataclass

from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader


@dataclass
class MetricsState:
    meter_provider: MeterProvider | None = None
    meter: object | None = None
    requests_counter: object | None = None
    failures_counter: object | None = None
    duration_histogram: object | None = None
    retrain_counter: object | None = None
    diagnosis_counter: object | None = None
    feature_store_counter: object | None = None
    pipeline_gauge: object | None = None
    initialized: bool = False


metrics_state = MetricsState()
_lock = threading.Lock()


def setup_telemetry(service_name: str = "quantumdx-api") -> MetricsState:
    """
    Initializes OpenTelemetry metrics with the Prometheus exporter.
    The PrometheusMetricReader exposes a scrape endpoint for Prometheus.
    Port/address can be configured via env vars recognized by the exporter.
    """
    with _lock:
        if metrics_state.initialized:
            return metrics_state

        resource = Resource.create({
            "service.name": service_name,
            "service.namespace": "quantumdx",
            "deployment.environment": os.getenv("APP_ENV", "dev"),
        })

        reader = PrometheusMetricReader()
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        meter = metrics.get_meter("quantumdx.observability", "1.0.0")

        metrics_state.meter_provider = provider
        metrics_state.meter = meter

        metrics_state.requests_counter = meter.create_counter(
            name="quantumdx_requests_total",
            description="Total number of observed operations",
            unit="1",
        )

        metrics_state.failures_counter = meter.create_counter(
            name="quantumdx_failures_total",
            description="Total number of failed operations",
            unit="1",
        )

        metrics_state.duration_histogram = meter.create_histogram(
            name="quantumdx_operation_duration_ms",
            description="Operation duration in milliseconds",
            unit="ms",
        )

        metrics_state.retrain_counter = meter.create_counter(
            name="quantumdx_retrain_total",
            description="Total number of retraining attempts",
            unit="1",
        )

        metrics_state.diagnosis_counter = meter.create_counter(
            name="quantumdx_diagnosis_total",
            description="Total number of diagnosis attempts",
            unit="1",
        )

        metrics_state.feature_store_counter = meter.create_counter(
            name="quantumdx_feature_store_writes_total",
            description="Total number of feature store writes",
            unit="1",
        )

        metrics_state.pipeline_gauge = meter.create_up_down_counter(
            name="quantumdx_pipeline_inflight",
            description="In-flight pipeline operations",
            unit="1",
        )

        metrics_state.initialized = True
        return metrics_state