from services.container import build_container

def test_retrain_command():
    container = build_container()
    container.command_service.submit_patient({
        "patient_id": "TR1",
        "clinic_id": "Clinic1",
        "age": 35,
        "sex": "M",
        "heart_rate": 110,
        "bp_systolic": 90,
        "bp_diastolic": 60,
        "wbc": 12000,
        "platelets": 50000,
        "diagnosis": 1,
    })
    container.command_service.submit_patient({
        "patient_id": "TR2",
        "clinic_id": "Clinic1",
        "age": 20,
        "sex": "F",
        "heart_rate": 80,
        "bp_systolic": 120,
        "bp_diastolic": 80,
        "wbc": 7000,
        "platelets": 200000,
        "diagnosis": 0,
    })
    container.retrain_service.request_retrain({"min_accuracy": 0.0})
    model = container.model_query_service.current_model()
    assert "model_type" in model
