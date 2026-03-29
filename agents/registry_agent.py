import pathlib
import json
from utils.config import model_registry_path
from .base import AgentResult

class RegistryAgent:
    def __init__(self, path: str | None = None):
        self.path = pathlib.Path(path or model_registry_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def promote(self, payload: dict) -> AgentResult:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return AgentResult(True, "Model promoted", payload)

    def current_model(self) -> dict:
        if not self.path.exists():
            return {"model_version": "bootstrap_reference", "model_type": "fallback", "weights": None, "intercept": None}
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)
