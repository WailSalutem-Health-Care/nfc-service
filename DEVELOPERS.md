# NFC Service - Development Team

This document acknowledges the developers who contributed to the NFC Service project.

## Team Members

- **Muhammad Faizan**
- **Roozbeh Kouchaki**
- **Fatemehalsadat Sabaghjafari**
- **Dipika Bhandari**

## Code Attribution

Every Python file in this project includes a docstring header with developer attribution. This ensures that when developers read the code or generate documentation, they can see who contributed to that module.

### Module Structure

All modules follow this documentation pattern:

```python
"""
Module Title - Clear Description

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Detailed explanation of what this module does and its responsibilities.
"""
```

## Project Components

### Core Application (`app/main.py`)
- FastAPI application initialization
- CORS configuration
- OpenTelemetry setup
- Consumer startup/shutdown

### Authentication & Authorization
- **`app/auth/auth.py`** - JWT token validation with Keycloak
- **`app/auth/dependencies.py`** - Authentication dependencies
- **`app/auth/permissions.py`** - Role-based access control

### NFC Management
- **`app/nfc/router.py`** - HTTP API endpoints
- **`app/nfc/services/nfc_service.py`** - Business logic layer
- **`app/nfc/repositories/nfc_repository.py`** - Data access layer
- **`app/nfc/schemas.py`** - Request/response models

### Database
- **`app/db/session.py`** - Session management with multi-tenant support
- **`app/db/models.py`** - SQLAlchemy ORM models
- **`app/db/base.py`** - Declarative base class

### Observability
- **`app/observability/telemetry.py`** - OpenTelemetry initialization
- **`app/observability/middleware.py`** - HTTP request tracing
- **`app/observability/logging_config.py`** - Structured JSON logging
- **`app/observability/metrics.py`** - Business metrics collection
- **`app/observability/database.py`** - Database query tracing

### Messaging
- **`app/messaging/rabbitmq.py`** - RabbitMQ event publishing
- **`app/messaging/consumer.py`** - Event consumer and handlers

### Configuration
- **`app/config.py`** - Application configuration management
- **`app/tenant/context.py`** - Multi-tenant context handling

### Database Migrations (`alembic/`)
- **`env.py`** - Alembic environment configuration
- **`versions/20260103_000001_create_nfc_tags.py`** - Initial schema
- **`versions/20260108_000002_add_nfc_tag_timestamps.py`** - Timestamp columns

### Tests
- **`tests/conftest.py`** - Pytest configuration and fixtures
- **`tests/nfc/test_nfc_service.py`** - Unit tests for business logic
- **`tests/integration/test_nfc_router.py`** - Integration tests for endpoints
- **`tests/e2e/test_nfc_workflow.py`** - End-to-end workflow tests

## Key Features Developed

✅ NFC tag lifecycle management (assign, deactivate, reactivate, replace)  
✅ Multi-tenant data isolation with PostgreSQL schemas  
✅ JWT authentication with Keycloak integration  
✅ OpenTelemetry observability (distributed tracing, metrics, logging)  
✅ RabbitMQ event publishing and consumption  
✅ Comprehensive test coverage (unit, integration, e2e)  
✅ Docker containerization  
✅ Kubernetes deployment manifests  
✅ API documentation  
✅ Database migrations with Alembic  

## Getting Started

For development setup, see the [README.md](README.md)

For API documentation, see the [NFC_API_DOCUMENTATION.md](NFC_API_DOCUMENTATION.md)

---

*Last Updated: February 22, 2026*
