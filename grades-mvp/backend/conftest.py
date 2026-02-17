"""
Fixtures de pytest para SGE Grades MVP
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User


# Database de prueba en memoria
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Engine de prueba
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Configurar pragmas para BD de prueba
@event.listens_for(test_engine, "connect")
def configure_test_connection(dbapi_connection, connection_record):
    """Configurar conexión de prueba"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

# Session de prueba
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture que proporciona una sesión de BD limpia para cada test
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=test_engine)
    
    # Crear sesión
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpiar todas las tablas después del test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente de prueba de FastAPI
    con BD de prueba inyectada y middlewares apropiados para testing
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Deshabilitar rate limiting en tests
    if hasattr(app.state, 'limiter'):
        app.state.limiter.enabled = False
    
    # TestClient usa 'testserver' como base_url que TrustedHostMiddleware bloquea
    # Lo solucionamos usando base_url con localhost
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client
    
    # Restaurar estado
    if hasattr(app.state, 'limiter'):
        app.state.limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Fixture que crea un usuario de prueba
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    user.set_password("TestPassword123")
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_superuser(db_session: Session) -> User:
    """
    Fixture que crea un superusuario de prueba
    """
    user = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    user.set_password("AdminPassword123")
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """
    Fixture que proporciona un token JWT válido
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """
    Fixture que proporciona headers con token de autenticación
    """
    return {"Authorization": f"Bearer {auth_token}"}
