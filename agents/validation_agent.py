from .base import AgentResult

REQUIRED_FIELDS = [
    "patient_id", "clinic_id", "age", "sex",
    "heart_rate", "bp_systolic", "bp_diastolic", "wbc", "platelets"
]

SYMPTOMS = [
    "fever", "muscle_pain", "jaundice", "vomiting", "confusion", "headache",
    "chills", "rigors", "nausea", "diarrhea", "cough", "bleeding",
    "prostration", "oliguria", "anuria", "conjunctival_suffusion",
    "muscle_tenderness",
]

class ValidationAgent:
    @staticmethod
    def validate(self, payload: dict) -> AgentResult:
        missing = [k for k in REQUIRED_FIELDS if k not in payload]
        if missing:
            return AgentResult(False, f"Missing fields: {missing}")
        cleaned = dict(payload)
        cleaned["patient_id"] = str(cleaned["patient_id"])
        cleaned["clinic_id"] = str(cleaned["clinic_id"])
        cleaned["sex"] = str(cleaned["sex"]).upper()
        if cleaned["sex"] not in {"M", "F", "MALE", "FEMALE"}:
            return AgentResult(False, "sex must be M/F or MALE/FEMALE")
        cleaned["sex"] = "F" if cleaned["sex"] in {"F", "FEMALE"} else "M"
        for field in ["age", "heart_rate", "bp_systolic", "bp_diastolic", "wbc", "platelets"]:
            cleaned[field] = float(cleaned[field])
        if cleaned["age"] < 0 or cleaned["age"] > 120:
            return AgentResult(False, "age out of range")
        if cleaned["platelets"] <= 0:
            return AgentResult(False, "platelets must be positive")
        for s in SYMPTOMS:
            cleaned[s] = bool(cleaned.get(s, False))
        if "diagnosis" in cleaned and cleaned["diagnosis"] is not None:
            cleaned["diagnosis"] = int(cleaned["diagnosis"])
            if cleaned["diagnosis"] not in [0, 1]:
                return AgentResult(False, "diagnosis must be 0 or 1")
        return AgentResult(True, "Patient validated", cleaned)
