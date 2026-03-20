from base import AgentResult

SYMPTOM_COLS = [
    "fever","muscle_pain","jaundice","vomiting","confusion","headache",
    "chills","rigors","nausea","diarrhea","cough","bleeding",
    "prostration","oliguria","anuria","conjunctival_suffusion",
    "muscle_tenderness"
]

NUMERIC_COLS = [
    "age","heart_rate","bp_systolic","bp_diastolic","wbc","platelets"
]

REQUIRED_COLS = [
    "age","sex","heart_rate","bp_systolic","bp_diastolic","wbc","platelets"
]


class ValidationAgent:
    @staticmethod
    def validate(self, patient: dict) -> AgentResult:
        cleaned = dict(patient)

        for col in REQUIRED_COLS:
            if col not in cleaned:
                return AgentResult(False, f"Missing field: {col}")

        # normalize sex
        if cleaned["sex"] in [1, "1"]:
            cleaned["sex"] = "M"
        elif cleaned["sex"] in [2, "2"]:
            cleaned["sex"] = "F"

        # numeric casting
        for col in NUMERIC_COLS:
            cleaned[col] = float(cleaned[col])

        # symptoms → 0/1
        for col in SYMPTOM_COLS:
            cleaned[col] = int(bool(cleaned.get(col, False)))

        return AgentResult(True, "Validated", cleaned)