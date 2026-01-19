"""
OpenTelemetry telemetry initialization for the NFC service.

This module sets up distributed tracing, metrics collection, and structured logging
with automatic export to the observability stack via OTLP.
"""

import logging
import os
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, SERVICE_NAMESPACE

logger = logging.getLogger(__name__)

# Global telemetry providers
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None


def get_resource() -> Resource:
    """
    Create OpenTelemetry resource with service identification attributes.
    
    Returns:
        Resource object with service metadata
    """
    service_name = os.getenv("OTEL_SERVICE_NAME", "nfc-service")
    service_version = os.getenv("SERVICE_VERSION", "1.0.0")
    service_namespace = os.getenv("SERVICE_NAMESPACE", "wailsalutem")
    
    # Parse additional resource attributes from environment
    additional_attrs = {}
    otel_resource_attrs = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
    if otel_resource_attrs:
        for pair in otel_resource_attrs.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                additional_attrs[key.strip()] = value.strip()
    
    resource_attrs = {
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        SERVICE_NAMESPACE: service_namespace,
        **additional_attrs,
    }
    
    return Resource.create(resource_attrs)


def init_telemetry() -> bool:
    """
    Initialize OpenTelemetry tracing and metrics providers.
    
    Sets up:
    - TracerProvider with OTLP exporter and batch span processor
    - MeterProvider with OTLP exporter and periodic metric reader
    - Resource attributes for service identification
    
    Returns:
        True if initialization succeeds, False otherwise
    """
    global _tracer_provider, _meter_provider
    
    try:
        # Get OTLP endpoint from environment
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://otel-collector.observability.svc.cluster.local:4317"
        )
        
        logger.info(f"Initializing OpenTelemetry with endpoint: {otlp_endpoint}")
        
        # Create resource with service identification
        resource = get_resource()
        
        # Initialize TracerProvider
        trace_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,  # Use insecure connection for internal cluster communication
        )
        
        _tracer_provider = TracerProvider(resource=resource)
        
        # Add BatchSpanProcessor for efficient trace export
        span_processor = BatchSpanProcessor(
            trace_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            export_timeout_millis=30000,
        )
        _tracer_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(_tracer_provider)
        
        logger.info("TracerProvider initialized successfully")
        
        # Initialize MeterProvider
        metric_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=True,
        )
        
        # Create PeriodicExportingMetricReader with 30-second export interval
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter,
            export_interval_millis=30000,  # 30 seconds
            export_timeout_millis=30000,
        )
        
        _meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
        
        # Set global meter provider
        metrics.set_meter_provider(_meter_provider)
        
        logger.info("MeterProvider initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)
        return False


def shutdown_telemetry():
    """
    Gracefully shutdown OpenTelemetry providers.
    
    Ensures all pending telemetry data is flushed before application exit.
    """
    global _tracer_provider, _meter_provider
    
    try:
        if _tracer_provider:
            logger.info("Shutting down TracerProvider...")
            _tracer_provider.shutdown()
            logger.info("TracerProvider shut down successfully")
        
        if _meter_provider:
            logger.info("Shutting down MeterProvider...")
            _meter_provider.shutdown()
            logger.info("MeterProvider shut down successfully")
            
    except Exception as e:
        logger.error(f"Error during telemetry shutdown: {e}", exc_info=True)


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for creating spans.
    
    Args:
        name: Name of the tracer (typically module name)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """
    Get a meter instance for recording metrics.
    
    Args:
        name: Name of the meter (typically module name)
    
    Returns:
        Meter instance
    """
    return metrics.get_meter(name)
