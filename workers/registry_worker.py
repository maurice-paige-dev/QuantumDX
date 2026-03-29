from agents.registry_agent import RegistryAgent
from events.envelope import build_event
from events.topics import MODEL_EVALUATED, MODEL_PROMOTED

class RegistryWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = RegistryAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(MODEL_EVALUATED, self.handle)

    def handle(self, event: dict) -> None:
        accuracy = float(event["payload"].get("accuracy", 0.0))
        if accuracy < 0.75:
            return
        payload = {
            "model_version": "v2-promoted",
            "model_type": "federated_linear_boundary",
            "weights": event["payload"]["weights"],
            "intercept": event["payload"]["intercept"],
            "metrics": {
                "accuracy": event["payload"].get("accuracy"),
                "sensitivity": event["payload"].get("sensitivity"),
                "specificity": event["payload"].get("specificity"),
                "n_eval": event["payload"].get("n_eval"),
            },
            "clinic_summary": event["payload"].get("clinic_summary", {}),
        }
        result = self.agent.promote(payload)
        if result.ok:
            self.bus.publish(MODEL_PROMOTED, build_event(MODEL_PROMOTED, "registry-worker", result.payload, trace_id=event["trace_id"]))
