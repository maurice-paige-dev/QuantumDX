import joblib
import numpy as np
from .base import AgentResult
from quantum_engine import predict_quantum_svm, bootstrap_svm_reference


class DiagnosisAgent:

    def __init__(self):
        self.model_path = "models/production.pkl"

    def diagnose(self, patient, encoded):

        try:
            model = joblib.load(self.model_path)
            w = np.array(model["model"]["weights"])
            b = model["model"]["intercept"]

            x = np.array(encoded)

            prob = 1 / (1 + np.exp(-(x @ w + b)))

        except:
            m = bootstrap_svm_reference()
            prob = predict_quantum_svm(patient, m)

        return AgentResult(True, "Diagnosed", {
            "probability": float(prob),
            "diagnosis": int(prob > 0.5)
        })