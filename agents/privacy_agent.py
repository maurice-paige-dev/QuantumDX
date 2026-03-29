from datetime import datetime
from .base import AgentResult


class PrivacyAgent:
    @staticmethod
    def redact(patient, encoded) -> AgentResult:
        return AgentResult(True, "Raw data removed", {
            "patient_id": patient["patient_id"],
            "clinic_id": patient.get("clinic_id", "default"),
            "encoded_vector": encoded["encoded_vector"],
            "diagnosis": patient.get("diagnosis"),
            "created_at": datetime.utcnow().isoformat()
        })