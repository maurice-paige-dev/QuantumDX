from __future__ import annotations

import uuid
import numpy as np

from .ingestion_agent import IngestionAgent
from .validation_agent import ValidationAgent
from .encoding_agent import EncodingAgent
from .privacy_agent import PrivacyAgent
from .feature_store_agent import FeatureStoreAgent
from .training_agent import TrainingAgent
from .federated_agent import FederatedAgent
from .evaluation_agent import EvaluationAgent
from .registry_agent import RegistryAgent
from .diagnosis_agent import DiagnosisAgent
from .base import AgentResult
from observability import get_logger, monitored, QuantumDxError


class QuantumDxPipeline:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.ingest = IngestionAgent()
        self.validate = ValidationAgent()
        self.encode = EncodingAgent()
        self.privacy = PrivacyAgent()
        self.store = FeatureStoreAgent()
        self.train = TrainingAgent()
        self.fed = FederatedAgent()
        self.eval = EvaluationAgent()
        self.registry = RegistryAgent()
        self.diagnose_agent = DiagnosisAgent()

    @monitored("QuantumDxPipeline", "add_patient")
    def add_patient(self, patient, trace_id: str | None = None):
        trace_id = trace_id or str(uuid.uuid4())
        try:
            r1 = self.ingest.ingest(patient)
            if not r1.ok:
                return r1

            r2 = self.validate.validate(r1.payload)
            if not r2.ok:
                return r2

            r3 = self.encode.encode(r2.payload)
            if not r3.ok:
                return r3

            r4 = self.privacy.redact(r2.payload, r3.payload)
            if not r4.ok:
                return r4

            return self.store.append(r4.payload)
        except Exception as exc:
            self.logger.exception(
                "Pipeline add_patient failed",
                extra={"trace_id": trace_id, "event": "pipeline_failure", "status": "failure"},
            )
            return AgentResult(False, f"Pipeline add_patient failed: {exc}")

    @monitored("QuantumDxPipeline", "label_patient")
    def label_patient(self, patient_id, diagnosis, trace_id: str | None = None):
        try:
            if diagnosis not in [0, 1]:
                return AgentResult(False, "diagnosis must be 0 or 1")
            return self.store.attach_label(patient_id, diagnosis)
        except Exception as exc:
            return AgentResult(False, f"Pipeline label_patient failed: {exc}")

    @monitored("QuantumDxPipeline", "retrain")
    def retrain(self, min_accuracy=0.75, trace_id: str | None = None):
        try:
            df = self.store.load()

            if df.empty:
                return AgentResult(False, "No training data available")

            models = {}
            for clinic, g in df.groupby("clinic_id"):
                r = self.train.train_local(g)
                if r.ok:
                    models[clinic] = r.payload

            if not models:
                return AgentResult(False, "No clinic had enough labeled data to train")

            fed = self.fed.aggregate(models)
            if not fed.ok:
                return fed

            metrics = self.eval.evaluate(
                df,
                np.array(fed.payload["weights"]),
                fed.payload["intercept"]
            )
            if not metrics.ok:
                return metrics

            accuracy = metrics.payload.get("accuracy", 0.0)
            if accuracy < min_accuracy:
                return AgentResult(
                    False,
                    f"Candidate rejected: accuracy {accuracy:.3f} < {min_accuracy:.3f}",
                    metrics.payload
                )

            return self.registry.save(fed.payload, metrics.payload)
        except Exception as exc:
            self.logger.exception(
                "Pipeline retrain failed",
                extra={"trace_id": trace_id, "event": "pipeline_failure", "status": "failure"},
            )
            return AgentResult(False, f"Pipeline retrain failed: {exc}")

    @monitored("QuantumDxPipeline", "diagnose_patient")
    def diagnose_patient(self, patient, trace_id: str | None = None):
        try:
            r1 = self.validate.validate(patient)
            if not r1.ok:
                return r1

            r2 = self.encode.encode(r1.payload)
            if not r2.ok:
                return r2

            return self.diagnose_agent.diagnose(r1.payload, r2.payload["encoded_vector"])
        except Exception as exc:
            return AgentResult(False, f"Pipeline diagnose_patient failed: {exc}")

    @monitored("QuantumDxPipeline", "current_model")
    def current_model(self, trace_id: str | None = None):
        try:
            prod = self.registry.load_production()

            if prod is None:
                return AgentResult(True, "No promoted model found", {
                    "model_version": "bootstrap_reference",
                    "model_type": "quantum_fallback",
                    "metrics": None
                })

            return AgentResult(True, "Production model loaded", {
                "model_version": prod.get("version"),
                "model_type": prod.get("model_type"),
                "metrics": prod.get("metrics")
            })
        except Exception as exc:
            return AgentResult(False, f"Pipeline current_model failed: {exc}")

    @monitored("QuantumDxPipeline", "feature_store_summary")
    def feature_store_summary(self, trace_id: str | None = None):
        try:
            df = self.store.load()

            if df.empty:
                return AgentResult(True, "Feature store empty", {
                    "n_records": 0,
                    "n_labeled": 0,
                    "clinics": []
                })

            clinics = sorted(df["clinic_id"].dropna().astype(str).unique().tolist())
            n_labeled = int(df["diagnosis"].notna().sum()) if "diagnosis" in df.columns else 0

            return AgentResult(True, "Feature store summary", {
                "n_records": int(len(df)),
                "n_labeled": n_labeled,
                "clinics": clinics
            })
        except Exception as exc:
            return AgentResult(False, f"Pipeline feature_store_summary failed: {exc}")