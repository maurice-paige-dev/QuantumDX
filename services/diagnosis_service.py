from agents.validation_agent import ValidationAgent
from agents.encoding_agent import EncodingAgent
from agents.registry_agent import RegistryAgent
from agents.diagnosis_agent import DiagnosisAgent

class DiagnosisService:
    def __init__(self, model_path: str = "/data/current_model.json"):
        self.validator = ValidationAgent()
        self.encoder = EncodingAgent()
        self.registry = RegistryAgent(path=model_path)
        self.agent = DiagnosisAgent()

    def diagnose(self, payload: dict) -> dict:
        valid = self.validator.validate(self.validator, payload)
        encoded = self.encoder.encode(self.encoder,valid.payload)
        model = self.registry.current_model()
        result = self.agent.diagnose({**encoded.payload, "model": model})
        return result.payload
