from __future__ import annotations

import json
import os

from confluent_kafka import Consumer

from agents import QuantumDxPipeline

from observability import configure_logging, get_logger, setup_telemetry

configure_logging()
setup_telemetry(service_name="quantumdx-kafka-consumer")
logger = get_logger("kafka_patient_consumer")

logger.info("Kafka consumer started", extra={"event": "consumer_start", "status": "started"})

TOPIC = os.getenv("KAFKA_TOPIC", "quantumdx.patient.intake")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "quantumdx-pipeline")
RETRAIN_EVERY = int(os.getenv("STREAM_RETRAIN_EVERY", "50"))
MIN_ACCURACY = float(os.getenv("STREAM_MIN_ACCURACY", "0.75"))

consumer = Consumer({
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest",
})

consumer.subscribe([TOPIC])

pipeline = QuantumDxPipeline()
ingested_since_last_train = 0

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(msg.error())
            continue

        patient = json.loads(msg.value().decode("utf-8"))
        result = pipeline.add_patient(patient)

        if result.ok:
            logger.info(
                "Kafka patient received",
                extra={
                    "event": "stream_record_received",
                    "status": "success",
                    "patient_id": patient.get("patient_id"),
                    "clinic_id": patient.get("clinic_id"),
                },
            )

            ingested_since_last_train += 1
        else:
            logger.exception(
                "Kafka ingestion failed",
                extra={
                    "event": "stream_record_failed",
                    "status": "failure",
                    "patient_id": patient.get("patient_id"),
                    "clinic_id": patient.get("clinic_id"),
                },
            )

        if ingested_since_last_train >= RETRAIN_EVERY:
            retrain_result = pipeline.retrain(min_accuracy=MIN_ACCURACY)
            print(retrain_result.message)
            if retrain_result.payload:
                print(retrain_result.payload)
            ingested_since_last_train = 0

finally:
    consumer.close()