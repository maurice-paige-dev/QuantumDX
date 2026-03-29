from collections import defaultdict
from .bus import EventBus

class InMemoryBus(EventBus):
    def __init__(self):
        self.handlers = defaultdict(list)
        self.event_log = []

    def publish(self, topic: str, event: dict) -> None:
        self.event_log.append((topic, event))
        for handler in list(self.handlers[topic]):
            handler(event)

    def subscribe(self, topic: str, handler) -> None:
        self.handlers[topic].append(handler)
