# Cloud Final Assignment - File Structure

This document maps the project files to the assignment requirements.

## ✅ Files Kept (Essential for Assignment)

### 1. Infrastructure & OpenShift Deployment

**Kubernetes/OpenShift Manifests (`k8s/`):**
- `k8s/base/deployment.yml` - Deployment with:
  - Container image configuration
  - Resource requirements (CPU/Memory requests & limits)
  - Environment variables
  - Health probes (readiness & liveness)
  - Rolling update strategy (resilience)
  - Persistent volume mounts
- `k8s/base/service.yml` - Service definition
- `k8s/base/route.yml` - OpenShift Route (TLS termination)
- `k8s/base/hpa.yml` - Horizontal Pod Autoscaler (auto-scaling)
- `k8s/base/pvc.yml` - Persistent Volume Claim (storage)
- `k8s/base/networkpolicy.yml` - Network policies (security)
- `k8s/base/serviceaccount.yml` - Service account
- `k8s/base/role.yml` - RBAC Role
- `k8s/base/rolebinding.yml` - RBAC RoleBinding
- `k8s/base/prometheusrule.yml` - Prometheus alerting rules
- `k8s/base/servicemonitor.yml` - ServiceMonitor for metrics scraping
- `k8s/config/configmap.yml` - ConfigMap (environment variables)
- `k8s/config/secret.yml` - Secrets (credentials)

**Container Image:**
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Local development setup

### 2. CI/CD Integration

**GitHub Actions:**
- `.github/workflows/deploy.yml` - CI/CD pipeline with:
  - Automated testing (pytest with JUnit & coverage)
  - OpenShift deployment
  - Rolling deployment strategy
  - Build trigger on code changes

### 3. Application Code (Python Application Factory Pattern)

**Core Application:**
- `app/main.py` - FastAPI application factory pattern
- `app/config.py` - Configuration management

**Authentication & Authorization:**
- `app/auth/auth.py` - Keycloak OAuth integration
- `app/auth/dependencies.py` - Auth dependencies
- `app/auth/permissions.py` - RBAC permissions
- `app/auth/permissions.yml` - Permission definitions

**Database Layer:**
- `app/db/base.py` - SQLAlchemy base
- `app/db/models.py` - Database models
- `app/db/session.py` - Database session management (multi-tenant)

**Business Logic (N-Tier Architecture):**
- `app/nfc/router.py` - API routes (presentation layer)
- `app/nfc/schemas.py` - Pydantic schemas
- `app/nfc/services/nfc_service.py` - Business logic (service layer)
- `app/nfc/repositories/nfc_repository.py` - Data access layer (repository pattern)

**Messaging:**
- `app/messaging/consumer.py` - RabbitMQ consumer (event-driven)
- `app/messaging/rabbitmq.py` - RabbitMQ connection & publishing

**Observability:**
- `app/observability/telemetry.py` - OpenTelemetry initialization
- `app/observability/middleware.py` - HTTP metrics & tracing middleware
- `app/observability/metrics.py` - Custom business metrics
- `app/observability/database.py` - Database instrumentation
- `app/observability/logging_config.py` - Structured logging

**Tenant Context:**
- `app/tenant/context.py` - Multi-tenant context management

### 4. Testing

**Test Files:**
- `tests/nfc/test_nfc_service.py` - Unit tests (service layer)
- `tests/integration/test_nfc_router.py` - Integration tests (API layer)
- `tests/e2e/test_nfc_workflow.py` - End-to-end tests
- `pytest.ini` - Pytest configuration

### 5. Database Migrations

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Alembic environment
- `alembic/versions/20260103_000001_create_nfc_tags.py` - Initial migration
- `alembic/versions/20260108_000002_add_nfc_tag_timestamps.py` - Timestamp migration

### 6. Dependencies & Configuration

- `requirements.txt` - Python dependencies (including OpenTelemetry, FastAPI, SQLAlchemy, etc.)
- `.gitignore` - Git ignore rules

### 7. Documentation

- `README.md` - Project documentation
- `OBSERVABILITY.md` - Observability implementation guide

## ❌ Files Removed

1. **`__pycache__/` directories** - Python bytecode cache (build artifacts, not source code)
2. **`*.pyc` files** - Compiled Python files (build artifacts)
3. **`nfc-api-documentation.yaml`** - Optional OpenAPI documentation (not required for assignment)

## 📋 Assignment Requirements Coverage

### Infrastructure
✅ **Cloud Environment**: OpenShift (on-premise/private cloud) - defined in k8s manifests
✅ **Deployment Requirements**: 
   - Container image (Dockerfile)
   - Environment variables (ConfigMap, Secret, deployment.yml)
   - Resource requirements (deployment.yml - CPU/Memory)

### Configuration
✅ **Resilience**: 
   - Rolling update strategy (deployment.yml)
   - Health probes (readiness & liveness)
   - Retry logic in RabbitMQ consumer
   - Replication sets (deployment replicas)

✅ **Authentication & Authorization**: 
   - Keycloak OAuth integration (app/auth/)
   - RBAC (k8s Role/RoleBinding, app permissions)

✅ **Storage**: 
   - Persistent Volume Claim (pvc.yml)
   - Dynamic provisioning (storageClassName)

### Code Audit
✅ **Separation of Concerns**: 
   - N-Tier architecture (router → service → repository)
   - Repository pattern
   - Dependency injection

✅ **Isolated & Testable**: 
   - Unit tests (service layer)
   - Integration tests (API layer)
   - E2E tests (workflow)

✅ **Python Application Factory**: 
   - `app/main.py` uses factory pattern (`create_app()`)

### DevOps
✅ **CI/CD Integration**: 
   - GitHub Actions workflow (`.github/workflows/deploy.yml`)
   - Automated testing
   - OpenShift deployment
   - Rolling deployment

### SRE
✅ **Test Report**: 
   - JUnit XML output (pytest.ini, CI/CD)
   - Coverage reports

✅ **Quality**: 
   - Automated testing (unit, integration, e2e)
   - Test configuration (pytest.ini)

✅ **Release Management**: 
   - Rolling deployment (deployment.yml strategy)
   - Rollback capability (OpenShift)
   - Deployment status monitoring

✅ **Monitoring**: 
   - Observability (OpenTelemetry)
   - Metrics (Prometheus, ServiceMonitor)
   - Logging (structured JSON logs)
   - Alerts (PrometheusRule)
   - Health endpoints

✅ **Scaling**: 
   - Horizontal Pod Autoscaler (hpa.yml)
   - Vertical scaling (resource limits)
   - Replica sets (deployment.yml)
