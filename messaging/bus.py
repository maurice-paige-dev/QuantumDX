from abc import ABC, abstractmethod
from typing import Callable

class EventBus(ABC):
    @abstractmethod
    def publish(self, topic: str, event: dict) -> None: ...
    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[dict], None]) -> None: ...
