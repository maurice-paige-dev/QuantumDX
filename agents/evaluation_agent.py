import math
from .base import AgentResult

class EvaluationAgent:
    @staticmethod
    def evaluate(self, payload: dict) -> AgentResult:
        model = payload["model"]
        rows = [r for r in payload["rows"] if r.get("diagnosis") is not None]
        if not rows:
            return AgentResult(False, "No labeled evaluation data")
        correct = tp = tn = fp = fn = 0
        for r in rows:
            score = sum(v * w for v, w in zip(r["encoded_vector"], model["weights"])) + model["intercept"]
            prob = 1.0 / (1.0 + math.exp(-score))
            pred = 1 if prob >= 0.5 else 0
            actual = int(r["diagnosis"])
            correct += int(pred == actual)
            tp += int(pred == 1 and actual == 1)
            tn += int(pred == 0 and actual == 0)
            fp += int(pred == 1 and actual == 0)
            fn += int(pred == 0 and actual == 1)
        return AgentResult(True, "Candidate evaluated", {
            "accuracy": correct / len(rows),
            "sensitivity": tp / (tp + fn) if (tp + fn) else 0.0,
            "specificity": tn / (tn + fp) if (tn + fp) else 0.0,
            "n_eval": len(rows),
        })
