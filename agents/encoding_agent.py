from core.quantum_engine import encode_16q
from .base import AgentResult

class EncodingAgent:
    @staticmethod
    def encode(self, payload: dict) -> AgentResult:
        encoded_vector = encode_16q(payload).astype(float).tolist()
        return AgentResult(True, "Patient encoded", {**payload, "encoded_vector": encoded_vector})
