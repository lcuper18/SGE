"""
Tests para Teacher Group Assignments API — Story 4.2
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.schedule import TeacherGroupAssignment


# ─────────────────────────────────────────────
# Fixtures helpers
# ─────────────────────────────────────────────

@pytest.fixture
def teacher(db_session: Session) -> User:
    """Crea un usuario teacher en la BD de prueba."""
    user = User(
        username="prof_martinez",
        email="martinez@school.edu",
        full_name="Roberto Martínez",
        role="teacher",
        is_active=True,
        is_superuser=False,
    )
    user.set_password("Pass1234!")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def teacher2(db_session: Session) -> User:
    """Segundo usuario teacher."""
    user = User(
        username="prof_garcia",
        email="garcia@school.edu",
        full_name="Ana García",
        role="teacher",
        is_active=True,
        is_superuser=False,
    )
    user.set_password("Pass1234!")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def group(client: TestClient) -> dict:
    """Crea un año → grado → grupo usando la API."""
    year = client.post(
        "/api/academic-years/", json={"year": 2026, "name": "Año 2026", "is_active": True}
    ).json()
    grade = client.post(
        "/api/grades/", json={"academic_year_id": year["id"], "level": 1, "name": "Primer Grado"}
    ).json()
    return client.post(
        "/api/groups/", json={"grade_id": grade["id"], "name": "Sección A", "capacity": 30}
    ).json()


@pytest.fixture
def group2(client: TestClient) -> dict:
    """Segundo grupo para tests de múltiples asignaciones."""
    year = client.post(
        "/api/academic-years/", json={"year": 2027, "name": "Año 2027", "is_active": False}
    ).json()
    grade = client.post(
        "/api/grades/", json={"academic_year_id": year["id"], "level": 2, "name": "Segundo Grado"}
    ).json()
    return client.post(
        "/api/groups/", json={"grade_id": grade["id"], "name": "Sección B", "capacity": 25}
    ).json()


def make_assignment(teacher_id: int, group_id: int, subject="Matemáticas", section="day"):
    return {
        "teacher_id": teacher_id,
        "group_id": group_id,
        "subject": subject,
        "section": section,
        "period_id": None,
        "is_active": True,
    }


# ─────────────────────────────────────────────
# CRUD básico
# ─────────────────────────────────────────────

class TestCreateAssignment:
    def test_create_success(self, client: TestClient, teacher: User, group: dict):
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["teacher_id"] == teacher.id
        assert data["group_id"] == group["id"]
        assert data["subject"] == "Matemáticas"
        assert data["section"] == "day"
        assert data["teacher_username"] == "prof_martinez"
        assert data["teacher_full_name"] == "Roberto Martínez"
        assert data["group_name"] == "Sección A"
        assert data["is_active"] is True

    def test_create_night_section(self, client: TestClient, teacher: User, group: dict):
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], section="night"),
        )
        assert resp.status_code == 201
        assert resp.json()["section"] == "night"

    def test_same_teacher_multiple_subjects_same_group(
        self, client: TestClient, teacher: User, group: dict
    ):
        """Un profesor puede impartir diferentes materias al mismo grupo."""
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Matemáticas"),
        )
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Física"),
        )
        assert resp.status_code == 201

    def test_duplicate_rejected(self, client: TestClient, teacher: User, group: dict):
        """Misma combinación teacher+group+subject+section debe dar 409."""
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        )
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        )
        assert resp.status_code == 409

    def test_teacher_not_found(self, client: TestClient, group: dict):
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(99999, group["id"]),
        )
        assert resp.status_code == 404

    def test_group_not_found(self, client: TestClient, teacher: User):
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, 99999),
        )
        assert resp.status_code == 404

    def test_invalid_role_rejected(self, client: TestClient, db_session: Session, group: dict):
        """Usuario con rol 'student' no puede ser asignado como profesor."""
        student_user = User(
            username="estudiant1",
            email="est1@school.edu",
            full_name="Estudiante Uno",
            role="student",
            is_active=True,
        )
        student_user.set_password("Pass1234!")
        db_session.add(student_user)
        db_session.commit()
        db_session.refresh(student_user)

        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(student_user.id, group["id"]),
        )
        assert resp.status_code == 422

    def test_blank_subject_rejected(self, client: TestClient, teacher: User, group: dict):
        resp = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="   "),
        )
        assert resp.status_code == 422


class TestReadAssignments:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/api/teacher-assignments/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_created(self, client: TestClient, teacher: User, group: dict):
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        )
        resp = client.get("/api/teacher-assignments/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_by_id(self, client: TestClient, teacher: User, group: dict):
        created = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        ).json()
        resp = client.get(f"/api/teacher-assignments/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_by_id_not_found(self, client: TestClient):
        assert client.get("/api/teacher-assignments/9999").status_code == 404

    def test_filter_by_teacher_id(self, client: TestClient, teacher: User, teacher2: User, group: dict):
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Matemáticas"),
        )
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher2.id, group["id"], subject="Lengua"),
        )
        resp = client.get(f"/api/teacher-assignments/?teacher_id={teacher.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["teacher_id"] == teacher.id

    def test_filter_by_group_id(self, client: TestClient, teacher: User, group: dict, group2: dict):
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Matemáticas"),
        )
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group2["id"], subject="Física"),
        )
        resp = client.get(f"/api/teacher-assignments/?group_id={group2['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["group_id"] == group2["id"]

    def test_filter_by_section(self, client: TestClient, teacher: User, group: dict):
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Mat", section="day"),
        )
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Mat", section="night"),
        )
        resp = client.get("/api/teacher-assignments/?section=night")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["section"] == "night"

    def test_filter_by_is_active(self, client: TestClient, teacher: User, group: dict):
        client.post(
            "/api/teacher-assignments/",
            json={**make_assignment(teacher.id, group["id"], subject="Activa"), "is_active": True},
        )
        client.post(
            "/api/teacher-assignments/",
            json={**make_assignment(teacher.id, group["id"], subject="Inactiva"), "is_active": False},
        )
        resp = client.get("/api/teacher-assignments/?is_active=false")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["is_active"] is False


class TestMyAssignments:
    def test_my_returns_only_own(self, client: TestClient, teacher: User, teacher2: User, group: dict):
        """GET /my/ con mock_admin (id=999) devuelve solo las suyas."""
        # Crear asignaciones para teacher y teacher2
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Matemáticas"),
        )
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher2.id, group["id"], subject="Lengua"),
        )
        # El cliente usa mock_admin (id=999) → no tiene asignaciones creadas
        resp = client.get("/api/teacher-assignments/my/")
        assert resp.status_code == 200
        # mock_admin id=999 no tiene asignaciones
        assert resp.json() == []


class TestUpdateAssignment:
    def test_update_subject(self, client: TestClient, teacher: User, group: dict):
        created = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        ).json()
        resp = client.put(
            f"/api/teacher-assignments/{created['id']}",
            json={"subject": "Física Avanzada"},
        )
        assert resp.status_code == 200
        assert resp.json()["subject"] == "Física Avanzada"

    def test_update_section(self, client: TestClient, teacher: User, group: dict):
        created = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        ).json()
        resp = client.put(
            f"/api/teacher-assignments/{created['id']}",
            json={"section": "night"},
        )
        assert resp.status_code == 200
        assert resp.json()["section"] == "night"

    def test_update_deactivate(self, client: TestClient, teacher: User, group: dict):
        created = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        ).json()
        resp = client.put(
            f"/api/teacher-assignments/{created['id']}",
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_update_not_found(self, client: TestClient):
        resp = client.put("/api/teacher-assignments/9999", json={"subject": "Historia"})
        assert resp.status_code == 404

    def test_update_causes_duplicate_rejected(
        self, client: TestClient, teacher: User, group: dict
    ):
        """Actualizar subject para que coincida con otra asignación existente debe dar 409."""
        client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Matemáticas"),
        )
        b = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"], subject="Física"),
        ).json()
        # Intentar cambiar Física → Matemáticas (ya existe)
        resp = client.put(
            f"/api/teacher-assignments/{b['id']}",
            json={"subject": "Matemáticas"},
        )
        assert resp.status_code == 409


class TestDeleteAssignment:
    def test_delete_success(self, client: TestClient, teacher: User, group: dict):
        created = client.post(
            "/api/teacher-assignments/",
            json=make_assignment(teacher.id, group["id"]),
        ).json()
        resp = client.delete(f"/api/teacher-assignments/{created['id']}")
        assert resp.status_code == 204
        assert client.get(f"/api/teacher-assignments/{created['id']}").status_code == 404

    def test_delete_not_found(self, client: TestClient):
        assert client.delete("/api/teacher-assignments/9999").status_code == 404


# ─────────────────────────────────────────────
# Permisos
# ─────────────────────────────────────────────

class TestAssignmentPermissions:
    def test_get_without_token_returns_401(self, real_client: TestClient):
        assert real_client.get("/api/teacher-assignments/").status_code == 401

    def test_post_without_token_returns_401(self, real_client: TestClient):
        assert real_client.post("/api/teacher-assignments/", json={}).status_code == 401

    def test_put_without_token_returns_401(self, real_client: TestClient):
        assert real_client.put("/api/teacher-assignments/1", json={}).status_code == 401

    def test_delete_without_token_returns_401(self, real_client: TestClient):
        assert real_client.delete("/api/teacher-assignments/1").status_code == 401

    def test_my_without_token_returns_401(self, real_client: TestClient):
        assert real_client.get("/api/teacher-assignments/my/").status_code == 401

    def test_teacher_can_list(self, real_client: TestClient, teacher_headers: dict):
        resp = real_client.get("/api/teacher-assignments/", headers=teacher_headers)
        assert resp.status_code == 200

    def test_teacher_can_get_my(self, real_client: TestClient, teacher_headers: dict):
        resp = real_client.get("/api/teacher-assignments/my/", headers=teacher_headers)
        assert resp.status_code == 200

    def test_teacher_cannot_create(
        self, real_client: TestClient, teacher_headers: dict
    ):
        """Un teacher no puede crear asignaciones (403)."""
        resp = real_client.post(
            "/api/teacher-assignments/",
            json={"teacher_id": 1, "group_id": 1, "subject": "X", "section": "day"},
            headers=teacher_headers,
        )
        assert resp.status_code == 403

    def test_teacher_cannot_delete(self, real_client: TestClient, teacher_headers: dict):
        resp = real_client.delete("/api/teacher-assignments/1", headers=teacher_headers)
        assert resp.status_code == 403
