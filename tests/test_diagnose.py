import services.container

def test_sync_diagnosis():
    container = services.container.build_container()
    result = container.diagnosis_service.diagnose({
        "patient_id": "D1",
        "clinic_id": "C1",
        "age": 40,
        "sex": "M",
        "heart_rate": 110,
        "bp_systolic": 90,
        "bp_diastolic": 60,
        "wbc": 12000,
        "platelets": 45000,
        "fever": True,
        "jaundice": True
    })
    assert "diagnosis" in result
    assert "probability" in result
