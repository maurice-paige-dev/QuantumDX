import numpy as np
from core.aggregator import FederatedAggregator
from .base import AgentResult

class TrainingAgent:
    @staticmethod
    def train_local(self, payload: dict) -> AgentResult:
        rows = [r for r in payload["rows"] if r.get("diagnosis") is not None]
        clinic_id = payload["clinic_id"]
        if len(rows) < 2:
            return AgentResult(False, f"Not enough labeled data for {clinic_id}")
        X = np.asarray([r["encoded_vector"] for r in rows], dtype=float)
        y = np.asarray([int(r["diagnosis"]) for r in rows], dtype=int)
        weights, intercept = FederatedAggregator.train_local_svm(X, y)
        return AgentResult(True, "Local model trained", {
            "clinic_id": clinic_id,
            "weights": weights.astype(float).tolist(),
            "intercept": float(intercept),
            "n_samples": int(len(rows)),
        })
