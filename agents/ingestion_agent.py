from base import AgentResult

class IngestionAgent:
    @staticmethod
    def ingest(self, patient: dict) -> AgentResult:
        return AgentResult(True, "Patient payload accepted", dict(patient))