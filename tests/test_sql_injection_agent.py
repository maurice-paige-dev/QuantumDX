def test_sql_ingestion_normalize_row():
    from agents.sql_ingestion_agent import SqlIngestionAgent

    row = {
        "patient_id": 123,
        "clinic_id": "Clinic_A",
        "age": 40,
        "sex": 1,
        "heart_rate": 100,
        "bp_systolic": 95,
        "bp_diastolic": 60,
        "wbc": 12000,
        "platelets": 50000,
        "fever": 1,
        "muscle_pain": 0,
        "jaundice": 1,
        "vomiting": 0,
        "confusion": 0,
        "headache": 1,
        "chills": 1,
        "rigors": 0,
        "nausea": 1,
        "diarrhea": 0,
        "cough": 0,
        "bleeding": 1,
        "prostration": 1,
        "oliguria": 1,
        "anuria": 0,
        "conjunctival_suffusion": 1,
        "muscle_tenderness": 1,
        "diagnosis": 1,
    }

    normalized = SqlIngestionAgent._normalize_row(row)

    assert normalized["patient_id"] == "123"
    assert normalized["sex"] == "M"
    assert normalized["fever"] is True
    assert normalized["muscle_pain"] is False
    assert normalized["diagnosis"] == 1


def test_sql_ingestion_recent_for_user(monkeypatch):
    from agents.sql_ingestion_agent import SqlIngestionAgent
    from agents.base import AgentResult

    class FakeSqlAgent:
        def get_patients_for_user(self, user_id, top=100, trace_id=None):
            return AgentResult(True, "ok", {
                "clinic_id": "Clinic_A",
                "records": [{
                    "patient_id": "PT_001",
                    "clinic_id": "Clinic_A",
                    "age": 42,
                    "sex": "M",
                    "heart_rate": 100,
                    "bp_systolic": 90,
                    "bp_diastolic": 60,
                    "wbc": 13000,
                    "platelets": 60000,
                    "fever": True,
                    "muscle_pain": True,
                    "jaundice": True,
                    "vomiting": False,
                    "confusion": False,
                    "headache": True,
                    "chills": True,
                    "rigors": False,
                    "nausea": True,
                    "diarrhea": False,
                    "cough": False,
                    "bleeding": False,
                    "prostration": True,
                    "oliguria": False,
                    "anuria": False,
                    "conjunctival_suffusion": True,
                    "muscle_tenderness": True,
                    "diagnosis": 1,
                }]
            })

    class FakePipeline:
        def add_patient(self, patient, trace_id=None):
            return AgentResult(True, "stored", {"patient_id": patient["patient_id"]})

    agent = SqlIngestionAgent(FakeSqlAgent())
    result = agent.ingest_recent_for_user(FakePipeline(), "user1", top=10, trace_id="t6")

    assert result.ok is True
    assert result.payload["loaded"] == 1
    assert result.payload["clinic_id"] == "Clinic_A"