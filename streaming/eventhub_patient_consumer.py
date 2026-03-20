from __future__ import annotations

import json
import os

from azure.eventhub import EventHubConsumerClient

from agents import QuantumDxPipeline
from observability import configure_logging, get_logger, setup_telemetry

configure_logging()
setup_telemetry(service_name="quantumdx-eventhub-consumer")
logger = get_logger("eventhub_patient_consumer")

CONNECTION_STR = os.getenv("EVENTHUB_CONNECTION_STR", "")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME", "quantumdx-patient-intake")
CONSUMER_GROUP = os.getenv("EVENTHUB_CONSUMER_GROUP", "$Default")
RETRAIN_EVERY = int(os.getenv("STREAM_RETRAIN_EVERY", "50"))
MIN_ACCURACY = float(os.getenv("STREAM_MIN_ACCURACY", "0.75"))

pipeline = QuantumDxPipeline()
ingested_since_last_train = 0


def on_event(partition_context, event):
    global ingested_since_last_train

    patient = json.loads(event.body_as_str())
    result = pipeline.add_patient(patient)

    if result.ok:
        print(f"Ingested patient {patient.get('patient_id')}")
        ingested_since_last_train += 1
    else:
        print(f"Failed patient {patient.get('patient_id')}: {result.message}")

    if ingested_since_last_train >= RETRAIN_EVERY:
        retrain_result = pipeline.retrain(min_accuracy=MIN_ACCURACY)
        print(retrain_result.message)
        if retrain_result.payload:
            print(retrain_result.payload)
        ingested_since_last_train = 0

    partition_context.update_checkpoint(event)


def main():
    if not CONNECTION_STR:
        raise ValueError("EVENTHUB_CONNECTION_STR is not set")

    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENTHUB_NAME,
    )

    with client:
        client.receive(
            on_event=on_event,
            starting_position="-1",
        )


if __name__ == "__main__":
    main()