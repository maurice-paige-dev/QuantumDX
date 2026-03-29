from agents.feature_store_agent import FeatureStoreAgent
from agents.training_agent import TrainingAgent
from events.envelope import build_event
from events.topics import MODEL_RETRAIN_REQUESTED, MODEL_TRAINED_LOCAL

class TrainingWorker:
    def __init__(self, bus):
        self.bus = bus
        self.store = FeatureStoreAgent()
        self.agent = TrainingAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(MODEL_RETRAIN_REQUESTED, self.handle)

    def handle(self, event: dict) -> None:
        rows = self.store.list_rows()
        clinics = sorted({r["clinic_id"] for r in rows if r.get("diagnosis") is not None})
        for clinic_id in clinics:
            payload = {"clinic_id": clinic_id, "rows": [r for r in rows if r["clinic_id"] == clinic_id]}
            result = self.agent.train_local(payload)
            if result.ok:
                self.bus.publish(MODEL_TRAINED_LOCAL, build_event(MODEL_TRAINED_LOCAL, "training-worker", result.payload, trace_id=event["trace_id"]))
