"""
Custom business metrics for NFC operations.

Provides counters, histograms, and gauges for tracking NFC-specific operations.
"""

"""
Custom Business Metrics for NFC Operations

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Provides counters, histograms, and gauges for tracking NFC-specific operations
    with automatic metric recording and context managers for operation tracking.
"""

import logging
import time
from typing import Literal
from contextlib import contextmanager

from app.observability.telemetry import get_meter

logger = logging.getLogger(__name__)

# Create meter for NFC metrics
meter = get_meter("nfc-service.business")

# NFC operation metrics
nfc_operations_counter = meter.create_counter(
    name="nfc_tag_operations_total",
    description="Total number of NFC tag operations",
    unit="1",
)

nfc_operation_duration_histogram = meter.create_histogram(
    name="nfc_operation_duration_milliseconds",
    description="Duration of NFC operations in milliseconds",
    unit="ms",
)

# Active connections gauge (using UpDownCounter as observable gauge)
nfc_active_connections = meter.create_up_down_counter(
    name="nfc_active_connections",
    description="Number of active NFC connections",
    unit="1",
)


class NFCMetrics:
    """
    Helper class for recording NFC-specific metrics.
    """
    
    @staticmethod
    def record_operation(
        operation_type: Literal["read", "write", "scan", "assign", "deactivate", "reactivate", "replace", "resolve"],
        status: Literal["success", "failure"],
        duration_ms: float = None,
    ):
        """
        Record an NFC tag operation.
        
        Args:
            operation_type: Type of operation (read, write, scan, assign, etc.)
            status: Operation status (success or failure)
            duration_ms: Optional duration in milliseconds
        """
        labels = {
            "operation_type": operation_type,
            "status": status,
        }
        
        # Increment operation counter
        nfc_operations_counter.add(1, attributes=labels)
        
        # Record duration if provided
        if duration_ms is not None:
            nfc_operation_duration_histogram.record(duration_ms, attributes=labels)
        
        logger.debug(f"Recorded NFC operation: {operation_type} - {status}")
    
    @staticmethod
    @contextmanager
    def track_operation(
        operation_type: Literal["read", "write", "scan", "assign", "deactivate", "reactivate", "replace", "resolve"]
    ):
        """
        Context manager for tracking NFC operation duration.
        
        Automatically records operation metrics with timing.
        
        Args:
            operation_type: Type of operation
        
        Yields:
            None
        
        Example:
            with NFCMetrics.track_operation("assign"):
                # Perform assignment operation
                service.assign_tag(...)
        """
        start_time = time.time()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "failure"
            logger.error(f"NFC operation {operation_type} failed: {e}")
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            NFCMetrics.record_operation(operation_type, status, duration_ms)
    
    @staticmethod
    def increment_active_connections(count: int = 1):
        """
        Increment the count of active NFC connections.
        
        Args:
            count: Number to increment (default: 1)
        """
        nfc_active_connections.add(count)
        logger.debug(f"Active NFC connections incremented by {count}")
    
    @staticmethod
    def decrement_active_connections(count: int = 1):
        """
        Decrement the count of active NFC connections.
        
        Args:
            count: Number to decrement (default: 1)
        """
        nfc_active_connections.add(-count)
        logger.debug(f"Active NFC connections decremented by {count}")


# Singleton instance for easy access
nfc_metrics = NFCMetrics()
