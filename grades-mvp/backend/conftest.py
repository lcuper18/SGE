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
from app.limiter import limiter as app_limiter
from app.models.user import User
from app.services.auth import get_current_user


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


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Resetea el storage del rate limiter antes de cada test para evitar
    que los contadores en memoria de un test afecten al siguiente.
    """
    if hasattr(app_limiter, '_storage') and hasattr(app_limiter._storage, 'reset'):
        try:
            app_limiter._storage.reset()
        except Exception:
            pass
    yield


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
    Fixture que proporciona un cliente de prueba de FastAPI.
    
    Overrides:
    - get_db → BD de prueba en memoria
    - get_current_user → admin mock (omite auth en tests de lógica de negocio)
    
    Para tests que necesitan evaluar autenticación/permisos reales,
    usar el fixture `real_client`.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Admin mock para saltar autenticación en tests de lógica de negocio
    mock_admin = User(
        id=999,
        username="mock_admin",
        email="mock@test.com",
        full_name="Mock Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )

    async def override_get_current_user():
        return mock_admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Deshabilitar rate limiting en tests
    app_limiter.enabled = False

    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client

    # Restaurar estado
    app_limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def real_client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente SIN overrides de autenticación.
    Úsalo en tests de permisos donde necesitas validar 401/403.
    El rate limiter se resetea antes de cada test para evitar falsos 429.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Resetear y deshabilitar el rate limiter para evitar falsos 429
    if hasattr(app_limiter, '_storage') and hasattr(app_limiter._storage, 'reset'):
        try:
            app_limiter._storage.reset()
        except Exception:
            pass
    app_limiter.enabled = False

    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client

    app_limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Fixture que crea un usuario de prueba (rol: teacher por defecto)
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        role="teacher",
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
    Fixture que crea un superusuario de prueba (rol: admin)
    """
    user = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        role="admin",
        is_active=True,
        is_superuser=True
    )
    user.set_password("AdminPassword123")
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Fixture: usuario con rol admin"""
    user = User(
        username="admin_user",
        email="admin_user@example.com",
        full_name="Admin User",
        role="admin",
        is_active=True,
        is_superuser=True
    )
    user.set_password("AdminPassword123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def coordinator_user(db_session: Session) -> User:
    """Fixture: usuario con rol coordinator"""
    user = User(
        username="coordinator_user",
        email="coordinator@example.com",
        full_name="Coordinator User",
        role="coordinator",
        is_active=True,
        is_superuser=False
    )
    user.set_password("CoordPassword123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def teacher_user(db_session: Session) -> User:
    """Fixture: usuario con rol teacher"""
    user = User(
        username="teacher_user",
        email="teacher@example.com",
        full_name="Teacher User",
        role="teacher",
        is_active=True,
        is_superuser=False
    )
    user.set_password("TeachPassword123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _get_token(client: TestClient, username: str, password: str) -> str:
    """Helper: obtiene token JWT para un usuario"""
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login falló para {username}: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def auth_token(real_client: TestClient, test_user: User) -> str:
    """
    Fixture que proporciona un token JWT válido (usuario teacher).
    Usa real_client para ejercitar autenticación real.
    """
    return _get_token(real_client, test_user.username, "TestPassword123")


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """
    Fixture que proporciona headers con token de autenticación (usuario teacher)
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(real_client: TestClient, admin_user: User) -> dict:
    """Headers de autenticación para admin"""
    token = _get_token(real_client, admin_user.username, "AdminPassword123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def coordinator_headers(real_client: TestClient, coordinator_user: User) -> dict:
    """Headers de autenticación para coordinator"""
    token = _get_token(real_client, coordinator_user.username, "CoordPassword123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher_headers(real_client: TestClient, teacher_user: User) -> dict:
    """Headers de autenticación para teacher"""
    token = _get_token(real_client, teacher_user.username, "TeachPassword123")
    return {"Authorization": f"Bearer {token}"}
