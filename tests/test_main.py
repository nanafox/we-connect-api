from fastapi.testclient import TestClient
import pytest
from posts_app.api.main import app
from fastapi import status


@pytest.fixture
def api_client():
    return TestClient(app)


def test_api_status(api_client):
    response = api_client.get("/api/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "OK"}


def test_unknown_route(api_client):
    response = api_client.get("/api/invalid")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not Found"}
