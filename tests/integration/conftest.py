import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from db.base import Base
from db import models  # noqa: F401  (registers every model on Base.metadata)
from db.session import get_db


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "integration.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # base_url must be https:// — the session cookie is Secure (by design), and a
    # plain http:// test client would silently drop it, breaking every
    # subsequent authenticated request.
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture()
def registered_user(client):
    payload = {"email": "user@example.com", "password": "s3cret!"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    return payload


@pytest.fixture()
def authenticated_client(client, registered_user):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    return client
