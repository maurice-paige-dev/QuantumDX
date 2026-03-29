import agents.feature_store_agent
from agents.registry_agent import RegistryAgent

class ModelQueryService:
    def __init__(self, model_path: str = "/data/current_model.json"):
        self.store = agents.feature_store_agent.FeatureStoreAgent()
        self.registry = RegistryAgent(path=model_path)

    def current_model(self) -> dict:
        return self.registry.current_model()

    @property
    def feature_store_summary(self) -> dict:
        return self.store.summary()
