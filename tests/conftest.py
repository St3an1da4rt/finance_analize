import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import config, database
from app.database import Base, get_db
from app.main import app
from app.services.extraction import ExtractedOperation


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    from app import models  # noqa: F401

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def client(session_factory, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(database, "SessionLocal", session_factory)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class FakeQueue:
    def __init__(self):
        self.ids = []

    def enqueue(self, operation_id):
        self.ids.append(operation_id)


@pytest.fixture(autouse=True)
def fake_queue(monkeypatch):
    """Uploads only record the job; tests run it explicitly via process_operation."""
    q = FakeQueue()
    monkeypatch.setattr("app.routes.images.extraction_queue", q)
    return q


@pytest.fixture(autouse=True)
def fake_extraction(monkeypatch):
    """Never call OpenAI from tests; individual tests may re-patch this."""
    result = ExtractedOperation(category=None, amount=None, description=None)
    monkeypatch.setattr("app.services.queue.extract_operation", lambda path: result)
