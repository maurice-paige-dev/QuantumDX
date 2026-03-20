import numpy as np
import pandas as pd


def test_pipeline_add_patient_success(monkeypatch, sample_patient, tmp_path):
    from agents.pipeline import QuantumDxPipeline
    from agents.base import AgentResult
    from agents.feature_store_agent import FeatureStoreAgent

    pipeline = QuantumDxPipeline()
    pipeline.store = FeatureStoreAgent(path=str(tmp_path / "store.jsonl"))

    monkeypatch.setattr(
        pipeline.encode,
        "encode",
        lambda patient: AgentResult(True, "encoded", {"encoded_vector": [0.1] * 16}),
    )

    result = pipeline.add_patient(sample_patient, trace_id="t1")

    assert result.ok is True
    assert result.message


def test_pipeline_label_patient_success(tmp_path):
    from agents.pipeline import QuantumDxPipeline
    from agents.feature_store_agent import FeatureStoreAgent

    pipeline = QuantumDxPipeline()
    pipeline.store = FeatureStoreAgent(path=str(tmp_path / "store.jsonl"))

    pipeline.store.append({
        "patient_id": "PT_001",
        "clinic_id": "Clinic_A",
        "encoded_vector": [0.1] * 16,
        "diagnosis": None,
    })

    result = pipeline.label_patient("PT_001", 1, trace_id="t2")

    assert result.ok is True
    assert result.payload["diagnosis"] == 1


def test_pipeline_retrain_rejects_when_no_data(tmp_path):
    from agents.pipeline import QuantumDxPipeline
    from agents.feature_store_agent import FeatureStoreAgent

    pipeline = QuantumDxPipeline()
    pipeline.store = FeatureStoreAgent(path=str(tmp_path / "empty.jsonl"))

    result = pipeline.retrain(min_accuracy=0.75, trace_id="t3")

    assert result.ok is False
    assert "No training data" in result.message


def test_pipeline_feature_store_summary(tmp_path):
    from agents.pipeline import QuantumDxPipeline
    from agents.feature_store_agent import FeatureStoreAgent

    pipeline = QuantumDxPipeline()
    pipeline.store = FeatureStoreAgent(path=str(tmp_path / "store.jsonl"))
    pipeline.store.append({
        "patient_id": "PT_001",
        "clinic_id": "Clinic_A",
        "encoded_vector": [0.1] * 16,
        "diagnosis": 1,
    })

    result = pipeline.feature_store_summary(trace_id="t4")

    assert result.ok is True
    assert result.payload["n_records"] == 1
    assert result.payload["n_labeled"] == 1


def test_pipeline_diagnose_patient(monkeypatch, sample_patient):
    from agents.pipeline import QuantumDxPipeline
    from agents.base import AgentResult

    pipeline = QuantumDxPipeline()

    monkeypatch.setattr(
        pipeline.encode,
        "encode",
        lambda patient: AgentResult(True, "encoded", {"encoded_vector": [0.1] * 16}),
    )
    monkeypatch.setattr(
        pipeline.diagnose_agent,
        "diagnose",
        lambda patient, encoded: AgentResult(True, "ok", {"diagnosis": 1, "probability": 0.88}),
    )

    result = pipeline.diagnose_patient(sample_patient, trace_id="t5")

    assert result.ok is True
    assert result.payload["diagnosis"] == 1