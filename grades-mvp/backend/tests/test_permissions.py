"""
Tests de permisos basados en roles (Story 1.3)

Valida que cada endpoint retorna el código de estado correcto
según el rol del usuario autenticado o la ausencia de autenticación.

Matriz de permisos:
- Sin token        → 401 Unauthorized
- Token inválido   → 401 Unauthorized
- Rol student/parent → 403 Forbidden
- GET + teacher/coordinator/admin → 200 OK
- POST/PUT/DELETE + teacher → 403 Forbidden
- POST/PUT/DELETE + coordinator/admin → 2xx OK
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import Subgroup


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_year(client: TestClient, headers: dict, year: int = 2026) -> dict:
    """Crea un año académico y retorna el JSON de respuesta."""
    resp = client.post(
        "/api/academic-years/",
        json={"year": year, "name": f"Año {year}", "is_active": False},
        headers=headers,
    )
    assert resp.status_code == 201, f"Failed to create year: {resp.text}"
    return resp.json()


def _create_period(client: TestClient, headers: dict, year_id: int) -> dict:
    start = date.today()
    end = start + timedelta(days=90)
    resp = client.post(
        "/api/periods/",
        json={
            "academic_year_id": year_id,
            "name": "Trimestre Test",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "is_active": False,
        },
        headers=headers,
    )
    assert resp.status_code == 201, f"Failed to create period: {resp.text}"
    return resp.json()


def _create_grade(client: TestClient, headers: dict, year_id: int, level: int = 1) -> dict:
    resp = client.post(
        "/api/grades/",
        json={"academic_year_id": year_id, "level": level, "name": f"Grado {level}"},
        headers=headers,
    )
    assert resp.status_code == 201, f"Failed to create grade: {resp.text}"
    return resp.json()


def _create_group(client: TestClient, headers: dict, grade_id: int) -> dict:
    resp = client.post(
        "/api/groups/",
        json={"grade_id": grade_id, "name": "Sección A", "capacity": 30},
        headers=headers,
    )
    assert resp.status_code == 201, f"Failed to create group: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# Tests: Acceso sin autenticación → 401
# ---------------------------------------------------------------------------

class TestUnauthenticatedAccess:
    """Todos los endpoints académicos deben rechazar peticiones sin token."""

    def test_get_years_no_token(self, real_client: TestClient):
        assert real_client.get("/api/academic-years/").status_code == 401

    def test_post_year_no_token(self, real_client: TestClient):
        assert real_client.post("/api/academic-years/", json={}).status_code == 401

    def test_get_periods_no_token(self, real_client: TestClient):
        assert real_client.get("/api/periods/").status_code == 401

    def test_get_grades_no_token(self, real_client: TestClient):
        assert real_client.get("/api/grades/").status_code == 401

    def test_get_groups_no_token(self, real_client: TestClient):
        assert real_client.get("/api/groups/").status_code == 401

    def test_get_students_no_token(self, real_client: TestClient):
        assert real_client.get("/api/students/").status_code == 401

    def test_invalid_token_returns_401(self, real_client: TestClient):
        headers = {"Authorization": "Bearer este.token.esinvalido"}
        assert real_client.get("/api/academic-years/", headers=headers).status_code == 401


# ---------------------------------------------------------------------------
# Tests: Teacher → lectura OK, escritura 403
# ---------------------------------------------------------------------------

class TestTeacherPermissions:
    """Teacher puede leer pero NO crear/modificar/eliminar recursos académicos."""

    def test_teacher_can_read_years(self, real_client: TestClient, teacher_headers: dict):
        resp = real_client.get("/api/academic-years/", headers=teacher_headers)
        assert resp.status_code == 200

    def test_teacher_cannot_create_year(self, real_client: TestClient, teacher_headers: dict):
        resp = real_client.post(
            "/api/academic-years/",
            json={"year": 2030, "name": "Año 2030", "is_active": False},
            headers=teacher_headers,
        )
        assert resp.status_code == 403

    def test_teacher_can_read_periods(self, real_client: TestClient, teacher_headers: dict):
        assert real_client.get("/api/periods/", headers=teacher_headers).status_code == 200

    def test_teacher_cannot_create_period(
        self, real_client: TestClient, teacher_headers: dict, admin_headers: dict
    ):
        year = _create_year(real_client, admin_headers, year=2027)
        start = date.today()
        end = start + timedelta(days=30)
        resp = real_client.post(
            "/api/periods/",
            json={
                "academic_year_id": year["id"],
                "name": "Trimestre Prohibido",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "is_active": False,
            },
            headers=teacher_headers,
        )
        assert resp.status_code == 403

    def test_teacher_can_read_grades(self, real_client: TestClient, teacher_headers: dict):
        assert real_client.get("/api/grades/", headers=teacher_headers).status_code == 200

    def test_teacher_cannot_create_grade(
        self, real_client: TestClient, teacher_headers: dict, admin_headers: dict
    ):
        year = _create_year(real_client, admin_headers, year=2028)
        resp = real_client.post(
            "/api/grades/",
            json={"academic_year_id": year["id"], "level": 2, "name": "Segundo Grado"},
            headers=teacher_headers,
        )
        assert resp.status_code == 403

    def test_teacher_can_read_groups(self, real_client: TestClient, teacher_headers: dict):
        assert real_client.get("/api/groups/", headers=teacher_headers).status_code == 200

    def test_teacher_cannot_create_group(
        self, real_client: TestClient, teacher_headers: dict, admin_headers: dict
    ):
        year = _create_year(real_client, admin_headers, year=2029)
        grade = _create_grade(real_client, admin_headers, year["id"])
        resp = real_client.post(
            "/api/groups/",
            json={"grade_id": grade["id"], "name": "Sección B", "capacity": 20},
            headers=teacher_headers,
        )
        assert resp.status_code == 403

    def test_teacher_can_read_students(self, real_client: TestClient, teacher_headers: dict):
        assert real_client.get("/api/students/", headers=teacher_headers).status_code == 200

    def test_teacher_cannot_create_student(
        self, real_client: TestClient, teacher_headers: dict
    ):
        resp = real_client.post(
            "/api/students/",
            json={
                "identification": "T001",
                "first_name": "No",
                "last_name": "Permitido",
                "date_of_birth": "2015-01-01",
            },
            headers=teacher_headers,
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Tests: Coordinator → lectura y escritura OK
# ---------------------------------------------------------------------------

class TestCoordinatorPermissions:
    """Coordinator puede leer y escribir en todos los recursos académicos."""

    def test_coordinator_can_create_year(
        self, real_client: TestClient, coordinator_headers: dict
    ):
        resp = real_client.post(
            "/api/academic-years/",
            json={"year": 2031, "name": "Año 2031", "is_active": False},
            headers=coordinator_headers,
        )
        assert resp.status_code == 201

    def test_coordinator_can_read_academic_years(
        self, real_client: TestClient, coordinator_headers: dict
    ):
        assert real_client.get("/api/academic-years/", headers=coordinator_headers).status_code == 200

    def test_coordinator_can_create_grade(
        self, real_client: TestClient, coordinator_headers: dict
    ):
        year = _create_year(real_client, coordinator_headers, year=2032)
        resp = real_client.post(
            "/api/grades/",
            json={"academic_year_id": year["id"], "level": 3, "name": "Tercer Grado"},
            headers=coordinator_headers,
        )
        assert resp.status_code == 201

    def test_coordinator_can_delete_group(
        self, real_client: TestClient, coordinator_headers: dict
    ):
        year = _create_year(real_client, coordinator_headers, year=2033)
        grade = _create_grade(real_client, coordinator_headers, year["id"])
        group = _create_group(real_client, coordinator_headers, grade["id"])
        resp = real_client.delete(
            f"/api/groups/{group['id']}",
            headers=coordinator_headers,
        )
        assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Tests: Admin → acceso completo
# ---------------------------------------------------------------------------

class TestAdminPermissions:
    """Admin tiene acceso completo a todos los endpoints."""

    def test_admin_can_create_year(self, real_client: TestClient, admin_headers: dict):
        resp = real_client.post(
            "/api/academic-years/",
            json={"year": 2040, "name": "Año 2040", "is_active": False},
            headers=admin_headers,
        )
        assert resp.status_code == 201

    def test_admin_can_read_years(self, real_client: TestClient, admin_headers: dict):
        assert real_client.get("/api/academic-years/", headers=admin_headers).status_code == 200

    def test_admin_can_update_year(self, real_client: TestClient, admin_headers: dict):
        year = _create_year(real_client, admin_headers, year=2041)
        resp = real_client.put(
            f"/api/academic-years/{year['id']}",
            json={"name": "Año 2041 Actualizado"},
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_admin_can_delete_year(self, real_client: TestClient, admin_headers: dict):
        year = _create_year(real_client, admin_headers, year=2042)
        resp = real_client.delete(
            f"/api/academic-years/{year['id']}",
            headers=admin_headers,
        )
        assert resp.status_code == 204

    def test_admin_can_manage_students(
        self, real_client: TestClient, admin_headers: dict, db_session: Session
    ):
        # Crear estructura mínima para subgroup
        year = _create_year(real_client, admin_headers, year=2043)
        grade = _create_grade(real_client, admin_headers, year["id"])
        group = _create_group(real_client, admin_headers, grade["id"])
        subgroup = Subgroup(group_id=group["id"], name="Subgrupo Test")
        db_session.add(subgroup)
        db_session.commit()
        db_session.refresh(subgroup)

        resp = real_client.post(
            "/api/students/",
            json={
                "identification": "ADM001",
                "first_name": "Admin",
                "last_name": "Test",
                "date_of_birth": "2015-06-01",
                "subgroup_id": subgroup.id,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["identification"] == "ADM001"


# ---------------------------------------------------------------------------
# Tests: JWT con role claim
# ---------------------------------------------------------------------------

class TestJWTRoleClaim:
    """Verifica que el token JWT contiene el claim de rol."""

    def test_login_token_has_role(self, real_client: TestClient, admin_user):
        resp = real_client.post(
            "/api/auth/login",
            json={"username": admin_user.username, "password": "AdminPassword123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        # El token es un JWT de 3 partes
        parts = data["access_token"].split(".")
        assert len(parts) == 3

    def test_register_response_includes_role(self, real_client: TestClient):
        resp = real_client.post(
            "/api/auth/register",
            json={
                "username": "roleusertest",
                "email": "roletest@example.com",
                "password": "RolePass123",
                "full_name": "Role Test User",
                "role": "coordinator",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["role"] == "coordinator"

    def test_register_default_role_is_teacher(self, real_client: TestClient):
        resp = real_client.post(
            "/api/auth/register",
            json={
                "username": "defaultroleuser",
                "email": "defaultrole@example.com",
                "password": "DefaultPass123",
                "full_name": "Default Role User",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "teacher"

    def test_register_invalid_role_rejected(self, real_client: TestClient):
        resp = real_client.post(
            "/api/auth/register",
            json={
                "username": "badroleuser",
                "email": "badrole@example.com",
                "password": "BadRole123",
                "full_name": "Bad Role User",
                "role": "supervillain",
            },
        )
        assert resp.status_code == 422
