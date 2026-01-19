"""
HTTP middleware for OpenTelemetry instrumentation.

Provides custom metrics and tracing for HTTP requests with proper naming conventions
compatible with the dashboard requirements.
"""

import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from app.observability.telemetry import get_meter

logger = logging.getLogger(__name__)

# Create meter for HTTP metrics
meter = get_meter("nfc-service.http")

# HTTP metrics with dashboard-compatible naming
http_requests_counter = meter.create_counter(
    name="http_server_requests_seconds_count",
    description="Total number of HTTP requests",
    unit="1",
)

http_duration_histogram = meter.create_histogram(
    name="http_server_duration_milliseconds",
    description="HTTP request duration in milliseconds",
    unit="ms",
)


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware for HTTP request tracing and metrics collection.
    
    Captures:
    - Request spans with detailed attributes
    - HTTP metrics (request count, duration)
    - Error tracking and status codes
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request with telemetry instrumentation.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in the chain
        
        Returns:
            HTTP response
        """
        # Skip telemetry for health checks to reduce noise
        if request.url.path == "/health":
            return await call_next(request)
        
        # Extract route pattern for metrics
        http_route = self._get_route_pattern(request)
        http_method = request.method
        
        # Start timing
        start_time = time.time()
        
        # Create span for request
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span(
            f"{http_method} {http_route}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            try:
                # Set span attributes
                span.set_attribute("http.method", http_method)
                span.set_attribute("http.route", http_route)
                span.set_attribute("http.target", str(request.url.path))
                span.set_attribute("http.url", str(request.url))
                span.set_attribute("http.scheme", request.url.scheme)
                span.set_attribute("service.name", "nfc-service")
                
                # Add query parameters if present
                if request.url.query:
                    span.set_attribute("http.query", request.url.query)
                
                # Process request
                response = await call_next(request)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Set span status
                http_status_code = response.status_code
                span.set_attribute("http.status_code", http_status_code)
                
                if http_status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                elif http_status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))
                
                # Record metrics with proper labels
                metric_labels = {
                    "http_method": http_method,
                    "http_route": http_route,
                    "http_status_code": str(http_status_code),
                    "service_name": "nfc-service",
                }
                
                # Increment request counter
                http_requests_counter.add(1, attributes=metric_labels)
                
                # Record duration histogram
                http_duration_histogram.record(duration_ms, attributes=metric_labels)
                
                return response
                
            except Exception as e:
                # Calculate duration even on error
                duration_ms = (time.time() - start_time) * 1000
                
                # Record exception in span
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("http.status_code", 500)
                
                # Record error metrics
                metric_labels = {
                    "http_method": http_method,
                    "http_route": http_route,
                    "http_status_code": "500",
                    "service_name": "nfc-service",
                }
                
                http_requests_counter.add(1, attributes=metric_labels)
                http_duration_histogram.record(duration_ms, attributes=metric_labels)
                
                logger.error(
                    f"Error processing request {http_method} {http_route}: {e}",
                    exc_info=True,
                )
                
                # Re-raise the exception
                raise
    
    def _get_route_pattern(self, request: Request) -> str:
        """
        Extract the route pattern from the request.
        
        Args:
            request: HTTP request
        
        Returns:
            Route pattern (e.g., "/nfc/{tag_id}") or path if no match
        """
        try:
            for route in request.app.routes:
                match, _ = route.matches(request.scope)
                if match == Match.FULL:
                    return route.path
            return request.url.path
        except Exception:
            return request.url.path
