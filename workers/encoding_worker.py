from agents.encoding_agent import EncodingAgent
from events.envelope import build_event
from events.topics import PATIENT_VALIDATED, PATIENT_ENCODED

class EncodingWorker:
    def __init__(self, bus):
        self.bus = bus
        self.agent = EncodingAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(PATIENT_VALIDATED, self.handle)

    def handle(self, event: dict) -> None:
        result = self.agent.encode(event["payload"])
        if result.ok:
            self.bus.publish(PATIENT_ENCODED, build_event(PATIENT_ENCODED, "encoding-worker", result.payload, trace_id=event["trace_id"]))
