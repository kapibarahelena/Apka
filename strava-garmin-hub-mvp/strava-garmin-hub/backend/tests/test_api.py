from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

def test_health_and_auth_boundary():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        assert client.get('/api/v1/dashboard').status_code == 401
        response = client.get('/api/v1/dashboard', headers={'X-Hub-API-Key': settings.hub_api_key})
        assert response.status_code == 200
        assert 'recent_activities' in response.json()
