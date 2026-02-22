"""
Observability Module - OpenTelemetry Integration

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Observability module for OpenTelemetry instrumentation.
    Provides centralized access to tracing and metrics components.
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
