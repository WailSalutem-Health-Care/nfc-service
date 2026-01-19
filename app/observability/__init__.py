"""
Observability module for OpenTelemetry instrumentation.
"""

from app.observability.telemetry import (
    init_telemetry,
    shutdown_telemetry,
    get_tracer,
    get_meter,
)

__all__ = [
    "init_telemetry",
    "shutdown_telemetry",
    "get_tracer",
    "get_meter",
]
