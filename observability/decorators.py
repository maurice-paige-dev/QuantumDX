from __future__ import annotations

import time
import uuid
from functools import wraps

from .logging_config import get_logger
from .telemetry import metrics_state


def monitored(agent_name: str, operation: str):
    def decorator(func):
        logger = get_logger(f"{agent_name}.{operation}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = kwargs.get("trace_id") or str(uuid.uuid4())
            started = time.perf_counter()

            attrs = {
                "agent": agent_name,
                "operation": operation,
            }

            if metrics_state.pipeline_gauge is not None:
                metrics_state.pipeline_gauge.add(1, attrs)

            if metrics_state.requests_counter is not None:
                metrics_state.requests_counter.add(1, attrs)

            logger.info(
                f"Starting {operation}",
                extra={
                    "event": "operation_start",
                    "agent": agent_name,
                    "pipeline_stage": operation,
                    "trace_id": trace_id,
                    "status": "started",
                },
            )

            try:
                result = func(*args, **kwargs)

                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                if metrics_state.duration_histogram is not None:
                    metrics_state.duration_histogram.record(duration_ms, attrs)

                logger.info(
                    f"Completed {operation}",
                    extra={
                        "event": "operation_complete",
                        "agent": agent_name,
                        "pipeline_stage": operation,
                        "trace_id": trace_id,
                        "status": "success",
                        "duration_ms": duration_ms,
                    },
                )

                return result

            except Exception as exc:
                duration_ms = round((time.perf_counter() - started) * 1000, 2)

                fail_attrs = {
                    "agent": agent_name,
                    "operation": operation,
                    "error_type": exc.__class__.__name__,
                }

                if metrics_state.failures_counter is not None:
                    metrics_state.failures_counter.add(1, fail_attrs)

                if metrics_state.duration_histogram is not None:
                    metrics_state.duration_histogram.record(duration_ms, attrs)

                logger.exception(
                    f"Failed {operation}: {exc}",
                    extra={
                        "event": "operation_failed",
                        "agent": agent_name,
                        "pipeline_stage": operation,
                        "trace_id": trace_id,
                        "status": "failure",
                        "duration_ms": duration_ms,
                        "error_type": exc.__class__.__name__,
                    },
                )
                raise

            finally:
                if metrics_state.pipeline_gauge is not None:
                    metrics_state.pipeline_gauge.add(-1, attrs)

        return wrapper

    return decorator