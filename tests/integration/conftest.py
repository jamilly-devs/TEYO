import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import bootstrap  # noqa: F401  (registers gamification/mascot domain-event subscribers)
from api.main import app
from db.base import Base
from db import models  # noqa: F401  (registers every model on Base.metadata)
from db.models.user import User
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


@pytest.fixture()
def client_db_session(client, tmp_path):
    """Sessão extra ligada ao mesmo arquivo SQLite do `client` HTTP —
    permite manipular timestamps históricos (ex.: `Task.updated_at`) que a
    API não expõe, necessário para testar o Motor de Padrões no nível do
    Orquestrador/conversa (equivalente ao que `db_session` já faz no nível
    de tools isoladas, ver test_tools_patterns.py). Depende de `client`
    para garantir que as tabelas já existem quando esta sessão abre."""
    db_path = tmp_path / "integration.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def db_session(tmp_path):
    """Sessão de banco isolada e em memória, para testar a camada de Tools
    direto (TESTING.md: 'Tools: cada tool testada isoladamente') sem
    precisar do transporte HTTP/autenticação da API."""
    db_path = tmp_path / "tools.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def user_id(db_session: Session) -> int:
    user = User(email="tools-user@example.com", password_hash="irrelevant-for-tool-tests")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id


@pytest.fixture()
def other_user_id(db_session: Session) -> int:
    """Um segundo usuário, para os testes de isolamento por user_id
    (BUSINESS_RULES.md #17, ARCHITECTURE.md)."""
    user = User(email="other-tools-user@example.com", password_hash="irrelevant-for-tool-tests")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id
