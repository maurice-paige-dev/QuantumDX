from __future__ import annotations

import os
import uuid

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from agents import QuantumDxPipeline, VaultAgent, SqlPatientDataAgent, SqlIngestionAgent
from observability import configure_logging, get_logger, setup_telemetry, metrics_state


configure_logging()
setup_telemetry(service_name=os.getenv("OTEL_SERVICE_NAME", "quantumdx-api"))
logger = get_logger("api")

def create_app() -> FastAPI:
    fapp = FastAPI(
        title="QuantumDx API",
        version="5.0.0",
        description="QuantumDx API with OpenTelemetry metrics and Prometheus scraping",
    )
    return fapp

app=create_app()

FastAPIInstrumentor.instrument_app(app)

pipeline = QuantumDxPipeline()

vault_agent: VaultAgent | None = None
sql_patient_agent: SqlPatientDataAgent | None = None
sql_ingestion_agent: SqlIngestionAgent | None = None

# 1. Validate required environment variables
vault_addr = os.getenv('VAULT_ADDR')
vault_token = os.getenv('VAULT_TOKEN')

if not vault_addr or not vault_token:
    logger.error("Vault/SQL integration failed: Missing VAULT_ADDR or VAULT_TOKEN",
                 extra={'event': 'startup', 'status': 'failure'})

try:
    vault_agent = VaultAgent()
    sql_patient_agent = SqlPatientDataAgent(vault_agent)
    sql_ingestion_agent = SqlIngestionAgent(sql_patient_agent)
    logger.info("Vault/SQL integration enabled", extra={"event": "startup", "status": "success"})
except Exception as e:
    logger.exception("Vault/SQL integration failed during startup: {e}", extra={"event": "startup", "status": "failure"})


class PatientPayload(BaseModel):
    patient_id: str | None = None
    clinic_id: str = "default_clinic"
    age: float
    sex: str | int
    heart_rate: float
    bp_systolic: float
    bp_diastolic: float
    wbc: float
    platelets: float
    fever: bool = False
    muscle_pain: bool = False
    jaundice: bool = False
    vomiting: bool = False
    confusion: bool = False
    headache: bool = False
    chills: bool = False
    rigors: bool = False
    nausea: bool = False
    diarrhea: bool = False
    cough: bool = False
    bleeding: bool = False
    prostration: bool = False
    oliguria: bool = False
    anuria: bool = False
    conjunctival_suffusion: bool = False
    muscle_tenderness: bool = False
    diagnosis: int | None = Field(default=None, description="Optional ground-truth label 0/1")


class LabelPayload(BaseModel):
    patient_id: str
    diagnosis: int = Field(..., ge=0, le=1)


class RetrainPayload(BaseModel):
    min_accuracy: float = Field(default=0.75, ge=0.0, le=1.0)


def _trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id", str(uuid.uuid4()))


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "vault_enabled": vault_agent is not None,
        "sql_enabled": sql_patient_agent is not None,
    }


@app.get("/models/current")
def get_current_model(request: Request) -> dict:
    trace_id = _trace_id(request)
    result = pipeline.current_model(trace_id=trace_id)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.message)
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.get("/feature-store/summary")
def get_feature_store_summary(request: Request) -> dict:
    trace_id = _trace_id(request)
    result = pipeline.feature_store_summary(trace_id=trace_id)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.message)
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.post("/patients")
def add_patient(payload: PatientPayload, request: Request) -> dict:
    trace_id = _trace_id(request)
    result = pipeline.add_patient(payload.model_dump(), trace_id=trace_id)
    if result.ok and metrics_state.feature_store_counter is not None:
        metrics_state.feature_store_counter.add(1, {"route": "/patients"})
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.message)
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.post("/patients/label")
def label_patient(payload: LabelPayload, request: Request) -> dict:
    trace_id = _trace_id(request)
    result = pipeline.label_patient(payload.patient_id, payload.diagnosis, trace_id=trace_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.message)
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.post("/diagnose")
def diagnose(payload: PatientPayload, request: Request) -> dict:
    trace_id = _trace_id(request)
    result = pipeline.diagnose_patient(payload.model_dump(), trace_id=trace_id)
    if result.ok and metrics_state.diagnosis_counter is not None:
        metrics_state.diagnosis_counter.add(1, {"route": "/diagnose"})
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.message)
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.post("/retrain")
def retrain(payload: RetrainPayload, request: Request) -> dict:
    trace_id = _trace_id(request)
    if metrics_state.retrain_counter is not None:
        metrics_state.retrain_counter.add(1, {"route": "/retrain"})
    result = pipeline.retrain(min_accuracy=payload.min_accuracy, trace_id=trace_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail={"message": result.message, "data": result.payload})
    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}


@app.post("/patients/ingest-from-sql/{user_id}")
def ingest_from_sql(user_id: str, request: Request, top: int = 100) -> dict:
    if sql_ingestion_agent is None:
        raise HTTPException(status_code=503, detail="SQL/Vault integration is not configured")

    trace_id = _trace_id(request)
    result = sql_ingestion_agent.ingest_recent_for_user(
        pipeline=pipeline,
        user_id=user_id,
        top=top,
        trace_id=trace_id,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.message)

    return {"ok": True, "trace_id": trace_id, "message": result.message, "data": result.payload}