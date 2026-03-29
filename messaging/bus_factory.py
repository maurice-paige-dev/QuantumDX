from utils.config import event_bus_mode
from .inmemory_bus import InMemoryBus
from .kafka_bus import KafkaBus

def build_event_bus():
    return KafkaBus() if event_bus_mode() == "kafka" else InMemoryBus()
