from aggregator import FederatedAggregator
from .base import AgentResult


class FederatedAgent:
    @staticmethod
    def aggregate(self, models):
        agg = FederatedAggregator(list(models.keys()))

        for k, m in models.items():
            agg.accept_weights(k, m["coef"], m["intercept"], m["n_samples"])

        w, b = agg.compute_global_boundary()

        return AgentResult(True, "Aggregated", {
            "weights": w.tolist(),
            "intercept": float(b)
        })