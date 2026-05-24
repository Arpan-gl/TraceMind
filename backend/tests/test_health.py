import os

from fastapi.testclient import TestClient


os.environ.setdefault("POSTGRES_URL", "postgresql+asyncpg://user:pass@localhost:5432/tracemind_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("INTERNAL_INGEST_SECRET", "test-ingest-secret")

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}