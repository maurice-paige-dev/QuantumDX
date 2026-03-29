from __future__ import annotations
import sys
from messaging.bus_factory import build_event_bus
from events.topics import PATIENT_RECEIVED, PATIENT_VALIDATED, PATIENT_ENCODED, PATIENT_REDACTED, MODEL_RETRAIN_REQUESTED, MODEL_TRAINED_LOCAL, MODEL_AGGREGATED, MODEL_EVALUATED
from workers.validation_worker import ValidationWorker
from workers.encoding_worker import EncodingWorker
from workers.privacy_worker import PrivacyWorker
from workers.feature_store_worker import FeatureStoreWorker
from workers.training_worker import TrainingWorker
from workers.federated_worker import FederatedWorker
from workers.evaluation_worker import EvaluationWorker
from workers.registry_worker import RegistryWorker

WORKERS = {
    "validation": (ValidationWorker, PATIENT_RECEIVED),
    "encoding": (EncodingWorker, PATIENT_VALIDATED),
    "privacy": (PrivacyWorker, PATIENT_ENCODED),
    "feature-store": (FeatureStoreWorker, PATIENT_REDACTED),
    "training": (TrainingWorker, MODEL_RETRAIN_REQUESTED),
    "federated": (FederatedWorker, MODEL_TRAINED_LOCAL),
    "evaluation": (EvaluationWorker, MODEL_AGGREGATED),
    "registry": (RegistryWorker, MODEL_EVALUATED),
}

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m workers.run_worker <worker-name>")
    name = sys.argv[1]
    if name not in WORKERS:
        raise SystemExit(f"Unknown worker: {name}")
    bus = build_event_bus()
    worker_cls, topic = WORKERS[name]
    worker = worker_cls(bus)
    if hasattr(bus, "subscribe_forever"):
        bus.subscribe_forever(topic, worker.handle, group_id=f"quantumdx.{name}")
    else:
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
