from agents.privacy_agent import PrivacyAgent
from events.envelope import build_event
from events.topics import PATIENT_ENCODED, PATIENT_REDACTED

class PrivacyWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = PrivacyAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(PATIENT_ENCODED, self.handle)

    def handle(self, event: dict) -> None:
        result = self.agent.redact(event["payload"])
        if result.ok:
            self.bus.publish(PATIENT_REDACTED, build_event(PATIENT_REDACTED, "privacy-worker", result.payload, trace_id=event["trace_id"]))
