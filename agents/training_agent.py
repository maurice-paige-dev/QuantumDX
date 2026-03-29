import numpy as np
from .base import AgentResult
from aggregator import FederatedAggregator


class TrainingAgent:
    @staticmethod
    def train_local(self, df):
        df = df.dropna(subset=["diagnosis"])

        if len(df) < 5:
            return AgentResult(False, "Not enough data")

        X = np.vstack(df["encoded_vector"])
        y = df["diagnosis"].values

        coef, intercept = FederatedAggregator.train_local_svm(X, y)

        return AgentResult(True, "Trained", {
            "coef": coef.tolist(),
            "intercept": float(intercept),
            "n_samples": len(df)
        })