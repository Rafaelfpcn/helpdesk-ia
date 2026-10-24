import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Banco SQLite EM MEMÓRIA, separado do banco real.
# StaticPool mantém a mesma conexão durante o teste (sem isso, cada conexão veria um banco em memória vazio diferente).
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    """Sessão direta no banco de teste, para testar services e scripts sem passar pela API."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def payload():
    """Dados fictícios válidos para abrir um chamado."""
    return {
        "requester_name": "Ana Souza Teste",
        "requester_email": "ana.teste@exemplo.com",
        "initial_category": "rede",
        "title": "VPN não conecta no notebook",
        "description": "Desde cedo a VPN não conecta e a internet está lenta.",
    }
