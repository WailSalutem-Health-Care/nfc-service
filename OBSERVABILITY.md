# OpenTelemetry Observability Guide

This document provides detailed information about the OpenTelemetry observability implementation in the NFC service.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Testing Telemetry](#testing-telemetry)
5. [Metrics Reference](#metrics-reference)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Architecture Overview

The NFC service uses OpenTelemetry for comprehensive observability:

```
┌─────────────────┐
│   NFC Service   │
│                 │
│  ┌───────────┐  │
│  │  Traces   │──┼──┐
│  └───────────┘  │  │
│  ┌───────────┐  │  │
│  │  Metrics  │──┼──┤    ┌──────────────────┐
│  └───────────┘  │  ├───▶│ OTLP Collector   │
│  ┌───────────┐  │  │    │ (port 4317/4318) │
│  │   Logs    │──┼──┘    └──────────────────┘
│  └───────────┘  │              │
└─────────────────┘              │
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              ┌──────────┐            ┌──────────┐
              │  Tempo   │            │Prometheus│
              │ (Traces) │            │(Metrics) │
              └──────────┘            └──────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                          ┌──────────┐
                          │ Grafana  │
                          │Dashboard │
                          └──────────┘
```

### Components

1. **Telemetry Module** (`app/observability/telemetry.py`)
   - Initializes TracerProvider and MeterProvider
   - Configures OTLP exporters
   - Manages resource attributes

2. **HTTP Middleware** (`app/observability/middleware.py`)
   - Captures HTTP request/response metrics
   - Creates spans for request tracing
   - Adds proper labels for dashboard compatibility

3. **Database Instrumentation** (`app/observability/database.py`)
   - Traces all SQLAlchemy database operations
   - Records query details and timing
   - Captures database errors

4. **Business Metrics** (`app/observability/metrics.py`)
   - NFC-specific operation metrics
   - Duration histograms
   - Active connection tracking

5. **Structured Logging** (`app/observability/logging_config.py`)
   - JSON formatted logs
   - Automatic trace_id and span_id injection
   - Correlation with distributed traces

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `opentelemetry-api` - OpenTelemetry API
- `opentelemetry-sdk` - OpenTelemetry SDK
- `opentelemetry-exporter-otlp-proto-grpc` - OTLP gRPC exporter
- `opentelemetry-instrumentation-fastapi` - FastAPI auto-instrumentation
- `opentelemetry-instrumentation-sqlalchemy` - SQLAlchemy instrumentation
- `opentelemetry-instrumentation-requests` - HTTP client instrumentation
- `opentelemetry-instrumentation-logging` - Logging instrumentation

### 2. Verify Installation

```bash
python -c "import opentelemetry; print(opentelemetry.__version__)"
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Required
export OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector.observability.svc.cluster.local:4317"
export OTEL_SERVICE_NAME="nfc-service"

# Optional
export OTEL_RESOURCE_ATTRIBUTES="service.namespace=wailsalutem,deployment.environment=production"
export OTEL_TRACES_SAMPLER="parentbased_always_on"
export SERVICE_VERSION="1.0.0"
export SERVICE_NAMESPACE="wailsalutem"
export LOG_LEVEL="INFO"
```

### Local Development

For local development without an OpenTelemetry collector:

```bash
# Point to a local collector (if running)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Or disable telemetry by pointing to non-existent endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:9999"
```

The service will log a warning but continue running normally if the collector is unavailable.

### Kubernetes Deployment

The Kubernetes deployment is pre-configured with OpenTelemetry settings in `k8s/base/deployment.yml`.

To deploy:

```bash
kubectl apply -f k8s/base/deployment.yml
```

## Testing Telemetry

### 1. Start the Service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see logs indicating telemetry initialization:

```json
{
  "timestamp": "2026-01-19T10:00:00.000000Z",
  "level": "INFO",
  "message": "Initializing OpenTelemetry with endpoint: http://otel-collector.observability.svc.cluster.local:4317",
  "service.name": "nfc-service"
}
```

### 2. Generate Test Traffic

Make some API requests:

```bash
# Health check (excluded from telemetry)
curl http://localhost:8000/health

# Get all NFC tags (generates telemetry)
curl -H "Authorization: Bearer <token>" http://localhost:8000/nfc/

# Resolve an NFC tag
curl -X POST http://localhost:8000/nfc/resolve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"tag_id": "test-tag-123"}'
```

### 3. Verify Telemetry Export

Check the service logs for telemetry export messages:

```bash
kubectl logs -f deployment/nfc-service -n wailsalutem-suite
```

### 4. View in Grafana

#### Traces (Tempo)

1. Open Grafana → Explore
2. Select "Tempo" datasource
3. Search for traces:
   - By service: `{ service.name="nfc-service" }`
   - By operation: `{ name="POST /nfc/resolve" }`
4. Click on a trace to view the waterfall

#### Metrics (Prometheus)

1. Open Grafana → Explore
2. Select "Prometheus" datasource
3. Run queries:

```promql
# Total requests
sum(rate(http_server_requests_seconds_count{service_name="nfc-service"}[5m]))

# Request rate by endpoint
sum(rate(http_server_requests_seconds_count{service_name="nfc-service"}[5m])) by (http_route)

# Average latency
sum(rate(http_server_duration_milliseconds_sum[5m])) / sum(rate(http_server_duration_milliseconds_count[5m]))

# Error rate
sum(rate(http_server_requests_seconds_count{service_name="nfc-service",http_status_code=~"5.."}[5m]))

# NFC operations by type
sum(rate(nfc_tag_operations_total[5m])) by (operation_type, status)
```

#### Logs (Loki)

1. Open Grafana → Explore
2. Select "Loki" datasource
3. Run queries:

```logql
# All logs
{service_name="nfc-service"}

# Errors only
{service_name="nfc-service"} | json | level="ERROR"

# Specific trace
{service_name="nfc-service"} | json | trace_id="<your-trace-id>"

# Logs from specific module
{service_name="nfc-service"} | json | logger=~"app.nfc.*"
```

## Metrics Reference

### HTTP Metrics

**`http_server_requests_seconds_count`**
- **Type**: Counter
- **Description**: Total number of HTTP requests
- **Labels**:
  - `http_method`: HTTP method (GET, POST, etc.)
  - `http_route`: Route pattern (e.g., `/nfc/{tag_id}`)
  - `http_status_code`: Response status code
  - `service_name`: Service identifier

**`http_server_duration_milliseconds`**
- **Type**: Histogram
- **Description**: HTTP request duration in milliseconds
- **Labels**: Same as above
- **Buckets**: Default histogram buckets

### NFC Business Metrics

**`nfc_tag_operations_total`**
- **Type**: Counter
- **Description**: Total number of NFC tag operations
- **Labels**:
  - `operation_type`: Type of operation (read, write, scan, assign, deactivate, reactivate, replace, resolve)
  - `status`: Operation status (success, failure)

**`nfc_operation_duration_milliseconds`**
- **Type**: Histogram
- **Description**: Duration of NFC operations in milliseconds
- **Labels**: Same as above
- **Buckets**: Default histogram buckets

**`nfc_active_connections`**
- **Type**: UpDownCounter
- **Description**: Number of active NFC connections
- **Labels**: None

### Example Grafana Dashboard Panels

#### 1. Request Rate Panel

```promql
sum(rate(http_server_requests_seconds_count{service_name="nfc-service"}[5m])) by (http_route)
```

#### 2. Error Rate Panel

```promql
sum(rate(http_server_requests_seconds_count{service_name="nfc-service",http_status_code=~"5.."}[5m]))
/ 
sum(rate(http_server_requests_seconds_count{service_name="nfc-service"}[5m]))
```

#### 3. Latency Panel (p95, p99)

```promql
histogram_quantile(0.95, sum(rate(http_server_duration_milliseconds_bucket[5m])) by (le, http_route))
```

#### 4. NFC Operations Panel

```promql
sum(rate(nfc_tag_operations_total[5m])) by (operation_type)
```

## Troubleshooting

### Telemetry Not Appearing in Grafana

1. **Check service logs**:
   ```bash
   kubectl logs deployment/nfc-service -n wailsalutem-suite | grep -i otel
   ```

2. **Verify collector is running**:
   ```bash
   kubectl get pods -n observability
   ```

3. **Test collector connectivity**:
   ```bash
   kubectl exec -it deployment/nfc-service -n wailsalutem-suite -- \
     curl http://otel-collector.observability.svc.cluster.local:4317
   ```

4. **Check collector logs**:
   ```bash
   kubectl logs deployment/otel-collector -n observability
   ```

### High Cardinality Metrics

If you experience high cardinality issues:

1. **Reduce label values**: Avoid using IDs in labels
2. **Implement sampling**: Use `traceidratio` sampler
3. **Configure metric filtering**: Drop unnecessary metrics at collector level

### Memory Issues

If the service has memory issues related to telemetry:

1. **Reduce batch sizes**: Lower `max_queue_size` and `max_export_batch_size`
2. **Increase export frequency**: Lower `export_interval_millis`
3. **Enable sampling**: Use a lower sampling rate

Configuration in `app/observability/telemetry.py`:

```python
span_processor = BatchSpanProcessor(
    trace_exporter,
    max_queue_size=512,      # Reduced from 2048
    max_export_batch_size=128,  # Reduced from 512
    export_timeout_millis=30000,
)
```

### Logs Missing trace_id

If logs don't show trace context:

1. **Verify logging is configured**: Check `configure_logging()` is called
2. **Check LoggingInstrumentor**: Ensure it's installed correctly
3. **Verify context propagation**: Ensure code runs within span context

## Best Practices

### 1. Span Naming

Use descriptive span names that indicate the operation:

```python
with tracer.start_as_current_span("nfc.assign_tag") as span:
    span.set_attribute("tag_id", tag_id)
    span.set_attribute("patient_id", patient_id)
    # ... operation
```

### 2. Error Handling

Always record exceptions in spans:

```python
try:
    # ... operation
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR, str(e)))
    raise
```

### 3. Metric Labels

Keep labels low-cardinality:

```python
# Good - bounded values
labels = {"operation_type": "assign", "status": "success"}

# Bad - unbounded values
labels = {"tag_id": tag_id}  # Infinite possible values
```

### 4. Sampling

Use parent-based sampling to maintain trace continuity:

```bash
export OTEL_TRACES_SAMPLER=parentbased_always_on
```

For high-traffic services, use ratio-based sampling:

```bash
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
```

### 5. Resource Attributes

Add meaningful resource attributes:

```bash
export OTEL_RESOURCE_ATTRIBUTES="
  service.namespace=wailsalutem,
  deployment.environment=production,
  k8s.cluster.name=wailsalutem-cluster,
  k8s.namespace.name=wailsalutem-suite
"
```

### 6. Log Levels

Use appropriate log levels:

- **DEBUG**: Verbose diagnostic information (development only)
- **INFO**: General informational messages
- **WARNING**: Potentially problematic situations
- **ERROR**: Error events that might still allow the application to continue

### 7. Health Check Exclusion

Exclude health checks from telemetry to reduce noise:

```python
if request.url.path == "/health":
    return await call_next(request)
```

This is already implemented in the middleware.

## Performance Impact

OpenTelemetry has minimal performance impact when properly configured:

- **CPU overhead**: ~2-5% for typical workloads
- **Memory overhead**: ~50-100MB for span buffering
- **Network overhead**: Batched exports minimize network calls

For production, monitor these metrics:

```promql
# Process CPU usage
process_cpu_seconds_total{service="nfc-service"}

# Process memory usage
process_resident_memory_bytes{service="nfc-service"}
```

## Further Reading

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/)
- [Grafana Tempo Documentation](https://grafana.com/docs/tempo/latest/)
- [Prometheus Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
