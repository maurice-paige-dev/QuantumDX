from agents.evaluation_agent import EvaluationAgent
from agents.feature_store_agent import FeatureStoreAgent
from events.envelope import build_event
from events.topics import MODEL_AGGREGATED, MODEL_EVALUATED

class EvaluationWorker:
    def __init__(self, bus):
        self.bus = bus
        self.store = FeatureStoreAgent()
        self.agent = EvaluationAgent()
        if hasattr(bus, "subscribe"):
            bus.subscribe(MODEL_AGGREGATED, self.handle)

    def handle(self, event: dict) -> None:
        rows = self.store.list_rows()
        result = self.agent.evaluate({"model": event["payload"], "rows": rows})
        if result.ok:
            payload = {**event["payload"], **result.payload}
            self.bus.publish(MODEL_EVALUATED, build_event(MODEL_EVALUATED, "evaluation-worker", payload, trace_id=event["trace_id"]))
