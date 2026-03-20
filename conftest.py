from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class DummyCounter:
    def __init__(self):
        self.calls = []

    def add(self, value, attrs=None):
        self.calls.append((value, attrs or {}))


class DummyHistogram:
    def __init__(self):
        self.calls = []

    def record(self, value, attrs=None):
        self.calls.append((value, attrs or {}))


class DummyMeter:
    def create_counter(self, *args, **kwargs):
        return DummyCounter()

    def create_histogram(self, *args, **kwargs):
        return DummyHistogram()

    def create_up_down_counter(self, *args, **kwargs):
        return DummyCounter()


class DummyMeterProvider:
    def __init__(self, *args, **kwargs):
        pass


class DummyPrometheusMetricReader:
    def __init__(self, *args, **kwargs):
        pass


class DummyResource:
    @staticmethod
    def create(attrs):
        return attrs


@pytest.fixture(autouse=True)
def stub_optional_modules(monkeypatch):
    """Provide lightweight stubs for optional packages so tests import cleanly."""

    # hvac stub
    hvac = types.ModuleType("hvac")

    class FakeHVACClient:
        def __init__(self, *args, **kwargs):
            self.secrets = types.SimpleNamespace(
                kv=types.SimpleNamespace(
                    v2=types.SimpleNamespace(
                        read_secret_version=lambda path: {"data": {"data": {}}}
                    )
                )
            )

        def is_authenticated(self):
            return True

    hvac.Client = FakeHVACClient
    monkeypatch.setitem(sys.modules, "hvac", hvac)

    # pyodbc stub
    pyodbc = types.ModuleType("pyodbc")

    class FakeConnection:
        def cursor(self):
            return types.SimpleNamespace()

        def close(self):
            return None

    pyodbc.connect = lambda *args, **kwargs: FakeConnection()
    monkeypatch.setitem(sys.modules, "pyodbc", pyodbc)

    # confluent_kafka stub
    ck = types.ModuleType("confluent_kafka")
    ck.Consumer = object
    monkeypatch.setitem(sys.modules, "confluent_kafka", ck)

    # azure event hub stub
    azure = types.ModuleType("azure")
    eventhub = types.ModuleType("azure.eventhub")
    eventhub.EventHubConsumerClient = object
    monkeypatch.setitem(sys.modules, "azure", azure)
    monkeypatch.setitem(sys.modules, "azure.eventhub", eventhub)

    # OpenTelemetry stubs
    otel = types.ModuleType("opentelemetry")
    otel_metrics = types.ModuleType("opentelemetry.metrics")
    otel_metrics.set_meter_provider = lambda provider: None
    otel_metrics.get_meter = lambda *args, **kwargs: DummyMeter()

    sdk_resources = types.ModuleType("opentelemetry.sdk.resources")
    sdk_resources.Resource = DummyResource

    sdk_metrics = types.ModuleType("opentelemetry.sdk.metrics")
    sdk_metrics.MeterProvider = DummyMeterProvider

    exporter_prom = types.ModuleType("opentelemetry.exporter.prometheus")
    exporter_prom.PrometheusMetricReader = DummyPrometheusMetricReader

    instr_fastapi = types.ModuleType("opentelemetry.instrumentation.fastapi")

    class DummyFastAPIInstrumentor:
        @staticmethod
        def instrument_app(app):
            return app

    instr_fastapi.FastAPIInstrumentor = DummyFastAPIInstrumentor

    monkeypatch.setitem(sys.modules, "opentelemetry", otel)
    monkeypatch.setitem(sys.modules, "opentelemetry.metrics", otel_metrics)
    monkeypatch.setitem(sys.modules, "opentelemetry.sdk.resources", sdk_resources)
    monkeypatch.setitem(sys.modules, "opentelemetry.sdk.metrics", sdk_metrics)
    monkeypatch.setitem(sys.modules, "opentelemetry.exporter.prometheus", exporter_prom)
    monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.fastapi", instr_fastapi)


@pytest.fixture
def sample_patient():
    return {
        "patient_id": "PT_001",
        "clinic_id": "Clinic_A",
        "age": 42,
        "sex": "M",
        "heart_rate": 108,
        "bp_systolic": 92,
        "bp_diastolic": 60,
        "wbc": 15000,
        "platelets": 45000,
        "fever": True,
        "muscle_pain": True,
        "jaundice": True,
        "vomiting": True,
        "confusion": False,
        "headache": True,
        "chills": True,
        "rigors": False,
        "nausea": True,
        "diarrhea": False,
        "cough": False,
        "bleeding": True,
        "prostration": True,
        "oliguria": True,
        "anuria": False,
        "conjunctival_suffusion": True,
        "muscle_tenderness": True,
        "diagnosis": 1,
    }


@pytest.fixture
def fake_dataframe():
    return pd.DataFrame([
        {"patient_id": "PT_001", "clinic_id": "Clinic_A", "encoded_vector": [0.1] * 16, "diagnosis": 1},
        {"patient_id": "PT_002", "clinic_id": "Clinic_A", "encoded_vector": [0.2] * 16, "diagnosis": 0},
        {"patient_id": "PT_003", "clinic_id": "Clinic_A", "encoded_vector": [0.3] * 16, "diagnosis": 1},
        {"patient_id": "PT_004", "clinic_id": "Clinic_A", "encoded_vector": [0.4] * 16, "diagnosis": 0},
        {"patient_id": "PT_005", "clinic_id": "Clinic_A", "encoded_vector": [0.5] * 16, "diagnosis": 1},
    ])


@pytest.fixture
def temp_feature_store(tmp_path):
    return str(tmp_path / "feature_store.jsonl")


@pytest.fixture
def client(monkeypatch):
    api = importlib.import_module("api")

    class FakePipeline:
        def current_model(self, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "ok", {"model_version": "v1", "model_type": "test", "metrics": None})

        def feature_store_summary(self, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "ok", {"n_records": 3, "n_labeled": 2, "clinics": ["Clinic_A"]})

        def add_patient(self, patient, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "stored", {"patient_id": patient.get("patient_id", "PT_X")})

        def label_patient(self, patient_id, diagnosis, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "labeled", {"patient_id": patient_id, "diagnosis": diagnosis})

        def diagnose_patient(self, patient, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "diagnosed", {"diagnosis": 1, "probability": 0.91})

        def retrain(self, min_accuracy=0.75, trace_id=None):
            from agents.base import AgentResult
            return AgentResult(True, "retrained", {"version": "20260320_100000"})

    monkeypatch.setattr(api, "pipeline", FakePipeline(), raising=True)
    return TestClient(api.app)
