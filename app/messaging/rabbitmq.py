import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

EXCHANGE_NAME = "nfc.events"
EXCHANGE_TYPE = "topic"

def get_channel():
    credentials = pika.PlainCredentials(
        RABBITMQ_USER,
        RABBITMQ_PASSWORD,
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
        )
    )

    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True,
    )

    return connection, channel


def publish_event(routing_key: str, payload: dict):
    connection, channel = get_channel()

    tz_name = os.getenv("APP_TIMEZONE") or os.getenv("TZ") or "Europe/Amsterdam"
    try:
        tz = ZoneInfo(tz_name)
        payload["timestamp"] = datetime.now(tz).isoformat()
    except ZoneInfoNotFoundError:
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,  # persistent
        ),
    )

    connection.close()
