from agents.feature_store_agent import FeatureStoreAgent
from events.envelope import build_event
from events.topics import PATIENT_REDACTED, FEATURE_STORED

class FeatureStoreWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = FeatureStoreAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(PATIENT_REDACTED, self.handle)

    def handle(self, event: dict) -> None:
        result = self.agent.store(event["payload"])
        if result.ok:
            self.bus.publish(FEATURE_STORED, build_event(FEATURE_STORED, "feature-store-worker", result.payload, trace_id=event["trace_id"]))
