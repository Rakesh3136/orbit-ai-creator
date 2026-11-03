from fastapi.testclient import TestClient
from aimn_api.main import app

client = TestClient(app)

def test_liveness_endpoint():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "service": "aimn-api"}

def test_system_endpoint_identifies_channel_management_stage():
    response = client.get("/api/v1/system")
    assert response.status_code == 200
    assert response.json()["stage"] == "channel-management-foundation"
