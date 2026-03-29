from core.aggregator import FederatedAggregator
from .base import AgentResult

class FederatedAgent:
    @staticmethod
    def aggregate(self, payload: dict) -> AgentResult:
        models = payload["models"]
        if not models:
            return AgentResult(False, "No local models")
        agg = FederatedAggregator([m["clinic_id"] for m in models])
        for m in models:
            agg.accept_weights(m["clinic_id"], m["weights"], m["intercept"], m["n_samples"])
        weights, intercept = agg.compute_global_boundary()
        return AgentResult(True, "Model aggregated", {
            "weights": weights.astype(float).tolist(),
            "intercept": float(intercept),
            "clinic_summary": agg.get_clinic_summary(),
        })
