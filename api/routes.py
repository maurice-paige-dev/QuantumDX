from fastapi import APIRouter, Depends
from .schemas import PatientCommand, RetrainCommand
from services.container import get_container

router = APIRouter()

@router.get("/health")
def health(container=Depends(get_container)) -> dict:
    return {"status": "ok", "service": "quantumdx-v2-merged-kafka"}

@router.post("/commands/patients")
def publish_patient(command: PatientCommand, container=Depends(get_container)) -> dict:
    event = container.command_service.submit_patient(command.model_dump())
    return {"accepted": True, "event": event}

@router.post("/commands/retrain")
def publish_retrain(command: RetrainCommand, container=Depends(get_container)) -> dict:
    event = container.retrain_service.request_retrain({"min_accuracy": command.min_accuracy})
    return {"accepted": True, "event": event}

@router.get("/queries/current-model")
def current_model(container=Depends(get_container)) -> dict:
    return container.model_query_service.current_model()

@router.get("/queries/feature-store")
def feature_store_summary(container=Depends(get_container)) -> dict:
    return container.model_query_service.feature_store_summary

@router.post("/diagnose-sync")
def diagnose_sync(command: PatientCommand, container=Depends(get_container)) -> dict:
    return container.diagnosis_service.diagnose(command.model_dump())
