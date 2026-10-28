from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Service

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def setup_function():
    with SessionLocal() as db:
        db.execute(delete(Service))
        db.commit()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "CloudOps Platform API"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_create_list_get_delete_service():
    payload = {
        "name": "payments-api",
        "environment": "dev",
        "status": "healthy",
    }

    created = client.post("/api/v1/services", json=payload)
    assert created.status_code == 201
    service_id = created.json()["id"]

    listed = client.get("/api/v1/services")
    assert listed.status_code == 200
    assert any(item["id"] == service_id for item in listed.json())

    fetched = client.get(f"/api/v1/services/{service_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "payments-api"

    deleted = client.delete(f"/api/v1/services/{service_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/services/{service_id}")
    assert missing.status_code == 404


def test_invalid_environment_rejected():
    response = client.post(
        "/api/v1/services",
        json={
            "name": "payments-api",
            "environment": "invalid",
            "status": "healthy",
        },
    )
    assert response.status_code == 422
