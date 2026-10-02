from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_users():
    response = client.get("/users")
    assert response.status_code == 200


def test_products():
    response = client.get("/products")
    assert response.status_code == 200


def test_protected_requires_auth():
    response = client.get("/protected")
    assert response.status_code == 401


def test_protected_valid_auth():
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer demo-token"},
    )
    assert response.status_code == 200


def test_rate_limit():
    response = client.get("/simulate-rate-limit")
    assert response.status_code == 429


def test_timeout():
    response = client.get("/simulate-timeout")
    assert response.status_code == 200
