import events.envelope
from events.topics import MODEL_RETRAIN_REQUESTED


class RetrainService:
    def __init__(self, bus):
        self.bus = bus

    def request_retrain(self, payload: dict | None = None, trace_id: str | None = None) -> dict:
        event = events.envelope.build_event(MODEL_RETRAIN_REQUESTED, "api", payload or {}, trace_id=trace_id)
        self.bus.publish(MODEL_RETRAIN_REQUESTED, event)
        return event
