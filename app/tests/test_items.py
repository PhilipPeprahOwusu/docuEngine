"""Test item endpoints"""
from fastapi.testclient import TestClient


def test_get_items(client: TestClient):
    """Test getting list of items"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_item_not_found(client: TestClient):
    """Test getting non-existent item returns 404"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
