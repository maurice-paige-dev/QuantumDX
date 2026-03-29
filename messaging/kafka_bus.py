from __future__ import annotations
import os
from confluent_kafka import Producer, Consumer
from events.serializers import dumps, loads
from .bus import EventBus

class KafkaBus(EventBus):
    def __init__(self, bootstrap_servers: str | None = None, client_id: str | None = None, group_prefix: str | None = None) -> None:
        self.bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.client_id = client_id or os.getenv("KAFKA_CLIENT_ID", "quantumdx")
        self.group_prefix = group_prefix or os.getenv("KAFKA_GROUP_PREFIX", "quantumdx")
        self._producer = Producer({"bootstrap.servers": self.bootstrap_servers, "client.id": self.client_id})

    def publish(self, topic: str, event: dict) -> None:
        self._producer.produce(topic=topic, value=dumps(event).encode("utf-8"))
        self._producer.flush()

    def subscribe(self, topic: str, handler) -> None:
        raise NotImplementedError("Use subscribe_forever() for Kafka consumers")

    def subscribe_forever(self, topic: str, handler, group_id: str | None = None) -> None:
        consumer = Consumer({
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": group_id or f"{self.group_prefix}.{topic}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        consumer.subscribe([topic])
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None or msg.error():
                    continue
                event = loads(msg.value().decode("utf-8"))
                handler(event)
                consumer.commit(msg)
        finally:
            consumer.close()
