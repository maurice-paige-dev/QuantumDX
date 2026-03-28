from .base import AgentResult
from quantum_engine import encode_16q


class EncodingAgent:
    @staticmethod
    def encode(patient: dict[str, any]) -> AgentResult:
        encoded = encode_16q(patient)
        return AgentResult(
            True,
            "Encoded with quantum_engine.encode_16q",
            {"encoded_vector": encoded.tolist()}
        )