def test_normalize_intake_row():
    from mlops.cdc_retrain_worker import normalize_intake_row

    row = {
        "patient_id": "PT_001",
        "clinic_id": "Clinic_A",
        "age": 40,
        "sex": 1,
        "heart_rate": 101,
        "bp_systolic": 91,
        "bp_diastolic": 61,
        "wbc": 12000,
        "platelets": 55000,
        "fever": 1,
        "muscle_pain": 1,
        "jaundice": 0,
        "vomiting": 0,
        "confusion": 0,
        "headache": 1,
        "chills": 1,
        "rigors": 0,
        "nausea": 1,
        "diarrhea": 0,
        "cough": 0,
        "bleeding": 0,
        "prostration": 1,
        "oliguria": 0,
        "anuria": 0,
        "conjunctival_suffusion": 1,
        "muscle_tenderness": 1,
        "diagnosis": 1,
    }

    normalized = normalize_intake_row(row)

    assert normalized["sex"] == "M"
    assert normalized["fever"] is True
    assert normalized["diagnosis"] == 1