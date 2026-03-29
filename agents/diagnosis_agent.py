import math
from core.quantum_engine import bootstrap_svm_reference, predict_quantum_svm
from .base import AgentResult

class DiagnosisAgent:
    def __init__(self):
        self._fallback_model = None

    def _fallback(self):
        if self._fallback_model is None:
            self._fallback_model = bootstrap_svm_reference()
        return self._fallback_model

    def diagnose(self, payload: dict) -> AgentResult:
        model = payload.get("model") or {}
        if model.get("weights") is not None and model.get("intercept") is not None:
            score = sum(v * w for v, w in zip(payload["encoded_vector"], model["weights"])) + model["intercept"]
            probability = 1.0 / (1.0 + math.exp(-score))
            diagnosis = 1 if probability >= 0.5 else 0
            return AgentResult(True, "Diagnosis completed", {
                "diagnosis": diagnosis,
                "probability": probability,
                "model_type": model.get("model_type", "federated_linear_boundary"),
                "model_version": model.get("model_version", "v2-promoted"),
            })
        probability = float(predict_quantum_svm(payload, self._fallback()))
        diagnosis = 1 if probability >= 0.5 else 0
        return AgentResult(True, "Diagnosis completed", {
            "diagnosis": diagnosis,
            "probability": probability,
            "model_type": "fallback_quantum",
            "model_version": "bootstrap_reference",
        })
