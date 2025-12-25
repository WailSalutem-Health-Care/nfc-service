import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=pika.PlainCredentials("wailsalutem", "wailsalutem"),
    )
)

channel = connection.channel()

channel.queue_declare(queue="care.nfc.resolved", durable=True)

def callback(ch, method, properties, body):
    print("Received:")
    print(json.loads(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue="care.nfc.resolved",
    on_message_callback=callback,
)

print("Waiting for messages...")
channel.start_consuming()
