from dataclasses import dataclass
from messaging.bus_factory import build_event_bus
from services.command_service import CommandService
from services.retrain_service import RetrainService
from services.diagnosis_service import DiagnosisService
from services.model_query_service import ModelQueryService

@dataclass
class Container:
    bus: object
    command_service: CommandService
    retrain_service: RetrainService
    diagnosis_service: DiagnosisService
    model_query_service: ModelQueryService

    def bootstrap(self) -> None:
        return None

_container = None

def build_container() -> Container:
    global _container
    if _container is not None:
        return _container
    bus = build_event_bus()
    _container = Container(
        bus=bus,
        command_service=CommandService(bus),
        retrain_service=RetrainService(bus),
        diagnosis_service=DiagnosisService(model_path="/data/current_model.json"),
        model_query_service=ModelQueryService(model_path="/data/current_model.json"),
    )
    return _container

def get_container():
    return build_container()
