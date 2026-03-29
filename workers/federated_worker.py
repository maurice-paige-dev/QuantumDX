from agents.federated_agent import FederatedAgent
from events.envelope import build_event
from events.topics import MODEL_TRAINED_LOCAL, MODEL_AGGREGATED

class FederatedWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = FederatedAgent()
        self.local_models = []
        if hasattr(bus, "subscribe"):
            bus.subscribe(MODEL_TRAINED_LOCAL, self.handle)

    def handle(self, event: dict) -> None:
        self.local_models.append(event["payload"])
        result = self.agent.aggregate({"models": self.local_models})
        if result.ok:
            self.bus.publish(MODEL_AGGREGATED, build_event(MODEL_AGGREGATED, "federated-worker", result.payload, trace_id=event["trace_id"]))
