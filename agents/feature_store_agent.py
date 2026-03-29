from feature_store.repository import build_feature_store_repository
from .base import AgentResult

class FeatureStoreAgent:
    def __init__(self):
        self.repo = build_feature_store_repository()

    def store(self, payload: dict) -> AgentResult:
        try:
            result = self.repo.append(payload)
            if result.get("deduped"):
                return AgentResult(True, "Feature already stored", {**payload, **result})
            return AgentResult(True, "Feature stored", {**payload, **result})
        except Exception as exc:
            return AgentResult(False, f"Feature store error: {exc}")

    def list_rows(self) -> list[dict]:
        return self.repo.load()

    def summary(self) -> dict:
        return self.repo.summary()
