"""Test user endpoints"""
from fastapi.testclient import TestClient


def test_get_users(client: TestClient):
    """Test getting list of users"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_not_found(client: TestClient):
    """Test getting non-existent user returns 404"""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
