import fastapi.testclient
from api.app import create_app

def test_health():
    client = fastapi.testclient.TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
