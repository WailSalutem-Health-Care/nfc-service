"""
Structured logging configuration with OpenTelemetry trace correlation.

Configures JSON logging with automatic trace_id and span_id injection.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter that includes trace context.
    
    Outputs structured logs in JSON format with trace_id and span_id
    for correlation with distributed traces.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with trace context.
        
        Args:
            record: Log record to format
        
        Returns:
            JSON string representation of the log
        """
        # Get current span context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Build log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service.name": "nfc-service",
        }
        
        # Add trace context if available
        if span_context.is_valid:
            log_entry["trace_id"] = format(span_context.trace_id, "032x")
            log_entry["span_id"] = format(span_context.span_id, "016x")
            log_entry["trace_flags"] = span_context.trace_flags
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "__dict__"):
            # Add custom fields that aren't part of standard LogRecord
            standard_fields = {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "__dict__", "span", "span_id", "trace_id"
            }
            
            for key, value in record.__dict__.items():
                if key not in standard_fields and not key.startswith("_"):
                    log_entry[key] = value
        
        # Add source location
        log_entry["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        return json.dumps(log_entry)


def configure_logging(log_level: str = "INFO"):
    """
    Configure structured logging with trace correlation.
    
    Sets up:
    - JSON formatted output
    - Automatic trace_id and span_id injection
    - OpenTelemetry logging instrumentation
    
    Args:
        log_level: Log level (DEBUG, INFO, WARN, ERROR)
    """
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Instrument logging to add trace context
    LoggingInstrumentor().instrument(set_logging_format=False)
    
    # Reduce noise from some libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    root_logger.info("Structured logging configured with trace correlation")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
