## NFC Service

NFC tag management service with comprehensive OpenTelemetry observability.

## Table of Contents

- [Migrations (Alembic)](#migrations-alembic)
- [Event Consumption (RabbitMQ)](#event-consumption-rabbitmq)
- [Observability](#observability)
  - [OpenTelemetry Integration](#opentelemetry-integration)
  - [Metrics](#metrics)
  - [Traces](#traces)
  - [Logs](#logs)
  - [Configuration](#configuration)
- [Environment Variables](#environment-variables)

## Migrations (Alembic)

Run migrations after setting DB env vars:

```bash
alembic upgrade head
```

## Event Consumption (RabbitMQ)

The service consumes patient/organization events to deactivate tags when upstream entities change.

Env vars:
- `RABBITMQ_HOST`
- `RABBITMQ_PORT`
- `RABBITMQ_USER`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_CONSUME_EXCHANGE` (default: `wailsalutem.events`)
- `RABBITMQ_CONSUME_QUEUE` (default: `nfc-tag-events`)
- `RABBITMQ_CONSUMER_ENABLED` (default: `true`)

## Observability

The NFC service is fully instrumented with OpenTelemetry, providing comprehensive observability through metrics, traces, and structured logs.

### OpenTelemetry Integration

The service automatically exports telemetry data to the observability stack via OTLP (OpenTelemetry Protocol):

- **Traces**: Exported to Grafana Tempo for distributed tracing
- **Metrics**: Exported to Prometheus for monitoring and alerting
- **Logs**: Structured JSON logs with trace correlation sent to Loki

**Observability Stack Endpoints:**
- OTLP Endpoint (gRPC): `http://otel-collector.observability.svc.cluster.local:4317`
- OTLP Endpoint (HTTP): `http://otel-collector.observability.svc.cluster.local:4318`

### Metrics

The service exposes the following metrics:

#### HTTP Metrics

| Metric Name | Type | Description | Labels |
|------------|------|-------------|--------|
| `http_server_requests_seconds_count` | Counter | Total number of HTTP requests | `http_method`, `http_route`, `http_status_code`, `service_name` |
| `http_server_duration_milliseconds` | Histogram | HTTP request duration in milliseconds | `http_method`, `http_route`, `http_status_code`, `service_name` |

#### NFC Business Metrics

| Metric Name | Type | Description | Labels |
|------------|------|-------------|--------|
| `nfc_tag_operations_total` | Counter | Total number of NFC tag operations | `operation_type`, `status` |
| `nfc_operation_duration_milliseconds` | Histogram | Duration of NFC operations in milliseconds | `operation_type`, `status` |
| `nfc_active_connections` | UpDownCounter | Number of active NFC connections | N/A |

**Operation Types:**
- `read` - Reading tag information
- `write` - Writing tag data
- `scan` - Scanning NFC tags
- `assign` - Assigning tags to patients
- `deactivate` - Deactivating tags
- `reactivate` - Reactivating tags
- `replace` - Replacing tags
- `resolve` - Resolving tag to patient

**Status Values:**
- `success` - Operation completed successfully
- `failure` - Operation failed

### Traces

Distributed tracing is automatically enabled for:

- **HTTP Requests**: All incoming HTTP requests create spans with detailed attributes
- **Database Operations**: All SQLAlchemy queries are traced with operation details
- **Business Logic**: Critical NFC operations are wrapped in spans

**Span Attributes:**

HTTP spans include:
- `http.method` - HTTP method (GET, POST, etc.)
- `http.route` - Route pattern (e.g., `/nfc/{tag_id}`)
- `http.target` - Full request path
- `http.status_code` - Response status code
- `service.name` - Service identifier

Database spans include:
- `db.system` - Database type (postgresql)
- `db.operation` - SQL operation (SELECT, INSERT, UPDATE, DELETE)
- `db.table` - Target table name
- `db.statement` - SQL statement (truncated for safety)

### Logs

The service uses structured JSON logging with automatic trace correlation:

**Log Format:**
```json
{
  "timestamp": "2026-01-19T10:30:45.123456Z",
  "level": "INFO",
  "logger": "app.nfc.services",
  "message": "NFC tag assigned successfully",
  "service.name": "nfc-service",
  "trace_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "span_id": "a1b2c3d4e5f6g7h8",
  "source": {
    "file": "/app/nfc/services/nfc_service.py",
    "line": 75,
    "function": "assign_tag"
  }
}
```

**Log Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially problematic situations
- `ERROR` - Error messages for failures and exceptions

**Trace Correlation:**
All logs automatically include `trace_id` and `span_id` when executed within a trace context, enabling seamless correlation between logs and traces in Grafana.

### Configuration

Observability features are configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://otel-collector.observability.svc.cluster.local:4317` |
| `OTEL_SERVICE_NAME` | Service name for telemetry | `nfc-service` |
| `OTEL_RESOURCE_ATTRIBUTES` | Additional resource attributes | `service.namespace=wailsalutem,deployment.environment=production` |
| `OTEL_TRACES_SAMPLER` | Trace sampling strategy | `parentbased_always_on` |
| `SERVICE_VERSION` | Service version | `1.0.0` |
| `SERVICE_NAMESPACE` | Service namespace | `wailsalutem` |
| `LOG_LEVEL` | Logging level | `INFO` |

**Sampling Strategies:**
- `always_on` - Sample all traces
- `always_off` - Don't sample any traces
- `parentbased_always_on` - Sample based on parent span (recommended)
- `traceidratio` - Sample based on trace ID ratio

### Viewing Telemetry

**Grafana Dashboards:**

1. **Traces (Tempo):**
   - Navigate to Grafana → Explore → Select Tempo datasource
   - Search by trace ID, service name, or operation
   - View distributed traces with span details

2. **Metrics (Prometheus):**
   - Navigate to Grafana → Explore → Select Prometheus datasource
   - Query metrics: `http_server_requests_seconds_count{service_name="nfc-service"}`
   - Create dashboards with panels for different metrics

3. **Logs (Loki):**
   - Navigate to Grafana → Explore → Select Loki datasource
   - Query logs: `{service_name="nfc-service"}`
   - Filter by trace_id to correlate with traces

**Example Queries:**

```promql
# HTTP request rate by endpoint
rate(http_server_requests_seconds_count{service_name="nfc-service"}[5m])

# Average request duration
rate(http_server_duration_milliseconds_sum[5m]) / rate(http_server_duration_milliseconds_count[5m])

# NFC operation success rate
sum(rate(nfc_tag_operations_total{status="success"}[5m])) / sum(rate(nfc_tag_operations_total[5m]))
```

```logql
# All logs for NFC service
{service_name="nfc-service"}

# Error logs only
{service_name="nfc-service"} | json | level="ERROR"

# Logs for a specific trace
{service_name="nfc-service"} | json | trace_id="your-trace-id-here"
```

### Graceful Shutdown

The service ensures all pending telemetry data is flushed before shutdown:

1. Consumer stops accepting new messages
2. In-flight requests complete
3. TracerProvider flushes pending spans
4. MeterProvider exports final metrics
5. Application exits

This guarantees no telemetry data is lost during deployments or restarts.

## Environment Variables

### Database
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port (default: `5432`)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

### RabbitMQ
- `RABBITMQ_HOST` - RabbitMQ host
- `RABBITMQ_PORT` - RabbitMQ port
- `RABBITMQ_USER` - RabbitMQ user
- `RABBITMQ_PASSWORD` - RabbitMQ password
- `RABBITMQ_CONSUME_EXCHANGE` - Exchange name (default: `wailsalutem.events`)
- `RABBITMQ_CONSUME_QUEUE` - Queue name (default: `nfc-tag-events`)
- `RABBITMQ_CONSUMER_ENABLED` - Enable consumer (default: `true`)

### OpenTelemetry
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTLP endpoint (default: `http://otel-collector.observability.svc.cluster.local:4317`)
- `OTEL_SERVICE_NAME` - Service name (default: `nfc-service`)
- `OTEL_RESOURCE_ATTRIBUTES` - Resource attributes
- `OTEL_TRACES_SAMPLER` - Sampling strategy (default: `parentbased_always_on`)
- `SERVICE_VERSION` - Service version (default: `1.0.0`)
- `SERVICE_NAMESPACE` - Namespace (default: `wailsalutem`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Application
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
