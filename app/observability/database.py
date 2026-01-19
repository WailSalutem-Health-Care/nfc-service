"""
Database instrumentation for OpenTelemetry tracing.

Provides automatic tracing for SQLAlchemy database operations.
"""

import logging
from sqlalchemy import Engine, event
from sqlalchemy.engine import Connection
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)


def instrument_database(engine: Engine):
    """
    Instrument SQLAlchemy engine with OpenTelemetry tracing.
    
    Creates spans for database operations with query details and timing.
    
    Args:
        engine: SQLAlchemy engine instance to instrument
    """
    tracer = trace.get_tracer(__name__)
    
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Start span before query execution."""
        # Store span in context
        span = tracer.start_span(
            name="db.query",
            kind=trace.SpanKind.CLIENT,
        )
        
        # Set database attributes
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", _extract_operation(statement))
        
        # Extract table name if possible
        table_name = _extract_table_name(statement)
        if table_name:
            span.set_attribute("db.table", table_name)
        
        # Store statement (truncate if too long for safety)
        statement_str = str(statement)[:1000]
        span.set_attribute("db.statement", statement_str)
        
        # Store span in context for later retrieval
        context.span = span
    
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """End span after query execution."""
        if hasattr(context, 'span'):
            span = context.span
            span.set_status(Status(StatusCode.OK))
            span.end()
    
    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context):
        """Record error in span if query fails."""
        context = exception_context.execution_context
        if hasattr(context, 'span'):
            span = context.span
            span.record_exception(exception_context.original_exception)
            span.set_status(Status(StatusCode.ERROR, str(exception_context.original_exception)))
            span.end()
    
    logger.info("Database instrumentation configured successfully")


def _extract_operation(statement: str) -> str:
    """
    Extract SQL operation type from statement.
    
    Args:
        statement: SQL statement
    
    Returns:
        Operation type (SELECT, INSERT, UPDATE, DELETE, etc.)
    """
    statement_str = str(statement).strip().upper()
    
    # Extract first word (operation type)
    if statement_str:
        first_word = statement_str.split()[0]
        return first_word
    
    return "UNKNOWN"


def _extract_table_name(statement: str) -> str:
    """
    Attempt to extract table name from SQL statement.
    
    Args:
        statement: SQL statement
    
    Returns:
        Table name if found, empty string otherwise
    """
    try:
        statement_str = str(statement).upper()
        
        # Simple pattern matching for common operations
        if "FROM " in statement_str:
            parts = statement_str.split("FROM ")
            if len(parts) > 1:
                table_part = parts[1].split()[0]
                return table_part.strip().lower()
        
        if "INTO " in statement_str:
            parts = statement_str.split("INTO ")
            if len(parts) > 1:
                table_part = parts[1].split()[0]
                return table_part.strip().lower()
        
        if "UPDATE " in statement_str:
            parts = statement_str.split("UPDATE ")
            if len(parts) > 1:
                table_part = parts[1].split()[0]
                return table_part.strip().lower()
        
        return ""
    except Exception:
        return ""
