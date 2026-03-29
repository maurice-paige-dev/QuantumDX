from .base import AgentResult

class IngestionAgent:
    @staticmethod
    def ingest(self, payload: dict) -> AgentResult:
        return AgentResult(True, "Patient received", dict(payload))
