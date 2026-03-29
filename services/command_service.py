from events.envelope import build_event
from events.topics import PATIENT_RECEIVED

class CommandService:
    def __init__(self, bus):
        self.bus = bus

    def submit_patient(self, payload: dict, trace_id: str | None = None) -> dict:
        event = build_event(PATIENT_RECEIVED, "api", payload, trace_id=trace_id, patient_id=payload.get("patient_id"), clinic_id=payload.get("clinic_id"))
        self.bus.publish(PATIENT_RECEIVED, event)
        return event
