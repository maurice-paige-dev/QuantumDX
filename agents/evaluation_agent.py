import numpy as np
from .base import AgentResult

class EvaluationAgent:
    @staticmethod
    def evaluate(self, df, w, b):
        df = df.dropna(subset=["diagnosis"])

        if len(df) == 0:
            return AgentResult(False, "No labeled evaluation data")

        X = np.vstack(df["encoded_vector"])
        y = df["diagnosis"].values

        preds = (X @ w + b > 0).astype(int)

        acc = float((preds == y).mean())

        return AgentResult(True, "Evaluated", {
            "accuracy": acc
        })