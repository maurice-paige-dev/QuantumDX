import joblib
from datetime import datetime, timezone
from pathlib import Path
from .base import AgentResult


class RegistryAgent:

    def __init__(self):
        self.dir = Path("models")
        self.dir.mkdir(exist_ok=True)

    def save(self, model, metrics):
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        obj = {"model": model, "metrics": metrics}

        path = self.dir / f"model_{ts}.pkl"
        joblib.dump(obj, path)

        joblib.dump(obj, self.dir / "production.pkl")

        return AgentResult(True, "Saved", {"version": ts})

    def load_production(self):
        path = self.dir / "production.pkl"
        if not path.exists():
            return None
        return joblib.load(path)