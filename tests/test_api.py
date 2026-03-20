def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_get_current_model(client):
    response = client.get("/models/current")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["model_version"] == "v1"


def test_feature_store_summary(client):
    response = client.get("/feature-store/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["n_records"] == 3


def test_add_patient(client, sample_patient):
    response = client.post("/patients", json=sample_patient)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True


def test_label_patient(client):
    response = client.post("/patients/label", json={"patient_id": "PT_001", "diagnosis": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["diagnosis"] == 1


def test_diagnose(client, sample_patient):
    response = client.post("/diagnose", json=sample_patient)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["diagnosis"] == 1


def test_retrain(client):
    response = client.post("/retrain", json={"min_accuracy": 0.8})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True