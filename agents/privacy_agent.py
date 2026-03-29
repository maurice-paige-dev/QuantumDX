from .base import AgentResult

class PrivacyAgent:
    @staticmethod
    def redact(self, payload: dict) -> AgentResult:
        kept = {
            "patient_id": payload["patient_id"],
            "clinic_id": payload["clinic_id"],
            "encoded_vector": payload["encoded_vector"],
            "diagnosis": payload.get("diagnosis"),
        }
        return AgentResult(True, "Patient redacted", kept)
