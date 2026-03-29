from agents.validation_agent import ValidationAgent
from events.envelope import build_event
from events.topics import PATIENT_RECEIVED, PATIENT_VALIDATED, PATIENT_VALIDATION_FAILED

class ValidationWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = ValidationAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(PATIENT_RECEIVED, self.handle)

    def handle(self, event: dict) -> None:
        result = self.agent.validate(event["payload"])
        topic = PATIENT_VALIDATED if result.ok else PATIENT_VALIDATION_FAILED
        next_event = build_event(topic, "validation-worker", result.payload or {"error": result.message}, trace_id=event["trace_id"])
        self.bus.publish(topic, next_event)
