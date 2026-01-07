## NFC Service

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
