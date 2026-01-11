import json
import os
import threading

from app.db.session import get_db_for_org
from app.messaging.rabbitmq import get_channel
from app.nfc.repositories import NfcRepository
from app.nfc.services import NfcService


CONSUME_EXCHANGE = os.getenv("RABBITMQ_CONSUME_EXCHANGE", "wailsalutem.events")
CONSUME_QUEUE = os.getenv("RABBITMQ_CONSUME_QUEUE", "nfc-tag-events")
CONSUME_ROUTING_KEYS = [
    "patient.created",
    "patient.deleted",
    "patient.status_changed",
    "organization.deleted",
    "organization.status_changed",
]
CONSUMER_ENABLED = os.getenv("RABBITMQ_CONSUMER_ENABLED", "true").lower() == "true"


class NfcEventConsumer:
    def __init__(self):
        self._connection = None
        self._channel = None
        self._thread = None

    def start(self):
        if not CONSUMER_ENABLED:
            return
        if self._thread and self._thread.is_alive():
            return

        try:
            connection, channel = get_channel()
        except Exception as exc:
            print(f"RabbitMQ consumer disabled: {exc}")
            return
        channel.exchange_declare(
            exchange=CONSUME_EXCHANGE,
            exchange_type="topic",
            durable=True,
        )

        channel.queue_declare(queue=CONSUME_QUEUE, durable=True)
        for routing_key in CONSUME_ROUTING_KEYS:
            channel.queue_bind(
                queue=CONSUME_QUEUE,
                exchange=CONSUME_EXCHANGE,
                routing_key=routing_key,
            )

        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(
            queue=CONSUME_QUEUE,
            on_message_callback=self._on_message,
            auto_ack=False,
        )

        self._connection = connection
        self._channel = channel

        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    def _consume(self):
        try:
            if self._channel:
                self._channel.start_consuming()
        except Exception:
            if self._channel and self._channel.is_open:
                try:
                    self._channel.stop_consuming()
                except Exception:
                    pass

    def stop(self):
        if self._channel and self._channel.is_open:
            try:
                self._channel.stop_consuming()
            except Exception:
                pass
        if self._connection and self._connection.is_open:
            try:
                self._connection.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)

    def _on_message(self, channel, method, properties, body):
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        event_type = payload.get("event_type") or method.routing_key
        data = payload.get("data") or {}

        try:
            if event_type == "patient.deleted":
                self._handle_patient_deleted(data)
            elif event_type == "patient.status_changed":
                self._handle_patient_status_changed(data)
            elif event_type == "organization.deleted":
                self._handle_org_deleted(data)
            elif event_type == "organization.status_changed":
                self._handle_org_status_changed(data)
            # patient.created -> no action needed

            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _handle_patient_deleted(self, data: dict):
        patient_id = data.get("patient_id")
        organization_id = data.get("organization_id")
        schema_name = data.get("schema_name")
        if not patient_id or not organization_id:
            return

        db = get_db_for_org(organization_id, schema_name)
        try:
            repository = NfcRepository(db)
            service = NfcService(repository, event_publisher=lambda **_: None)
            service.deactivate_tags_for_patient(patient_id)
        finally:
            db.close()

    def _handle_patient_status_changed(self, data: dict):
        patient_id = data.get("patient_id")
        organization_id = data.get("organization_id")
        new_status = data.get("new_status")
        schema_name = data.get("schema_name")
        if not patient_id or not organization_id:
            return
        if new_status == "active":
            return

        db = get_db_for_org(organization_id, schema_name)
        try:
            repository = NfcRepository(db)
            service = NfcService(repository, event_publisher=lambda **_: None)
            service.deactivate_tags_for_patient(patient_id)
        finally:
            db.close()

    def _handle_org_deleted(self, data: dict):
        organization_id = data.get("organization_id")
        schema_name = data.get("schema_name")
        if not organization_id:
            return

        db = get_db_for_org(organization_id, schema_name)
        try:
            repository = NfcRepository(db)
            service = NfcService(repository, event_publisher=lambda **_: None)
            service.deactivate_all_tags()
        finally:
            db.close()

    def _handle_org_status_changed(self, data: dict):
        organization_id = data.get("organization_id")
        new_status = data.get("new_status")
        schema_name = data.get("schema_name")
        if not organization_id:
            return
        if new_status == "active":
            return

        db = get_db_for_org(organization_id, schema_name)
        try:
            repository = NfcRepository(db)
            service = NfcService(repository, event_publisher=lambda **_: None)
            service.deactivate_all_tags()
        finally:
            db.close()
