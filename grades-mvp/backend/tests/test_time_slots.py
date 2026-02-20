"""
Tests para Time Slots API — Story 4.1
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.schedule import TimeSlot, SlotType, LessonType, Section, Weekday


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_lesson(
    name="Bloque 1",
    start="07:00",
    end="07:40",
    slot_type="lesson",
    lesson_type="academic",
    weekday=0,
    section="day",
    is_active=True,
):
    return {
        "name": name,
        "start_time": start,
        "end_time": end,
        "slot_type": slot_type,
        "lesson_type": lesson_type,
        "weekday": weekday,
        "section": section,
        "is_active": is_active,
    }


def make_break(name="Recreo", start="09:00", end="09:20", weekday=0, section="day"):
    return {
        "name": name,
        "start_time": start,
        "end_time": end,
        "slot_type": "break",
        "lesson_type": None,
        "weekday": weekday,
        "section": section,
        "is_active": True,
    }


# ─────────────────────────────────────────────
# CRUD básico
# ─────────────────────────────────────────────

class TestCreateTimeSlot:
    def test_create_academic_lesson(self, client: TestClient):
        resp = client.post("/api/time-slots/", json=make_lesson())
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Bloque 1"
        assert data["slot_type"] == "lesson"
        assert data["lesson_type"] == "academic"
        assert data["duration_minutes"] == 40
        assert data["academic_equivalent_minutes"] == 40.0
        assert data["weekday"] == 0
        assert data["section"] == "day"

    def test_create_technical_lesson(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(
                name="Bloque T1",
                start="12:20",
                end="13:20",
                lesson_type="technical",
            ),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["lesson_type"] == "technical"
        assert data["duration_minutes"] == 60
        assert data["academic_equivalent_minutes"] == 90.0  # 60 × 1.5

    def test_create_break(self, client: TestClient):
        resp = client.post("/api/time-slots/", json=make_break())
        assert resp.status_code == 201
        data = resp.json()
        assert data["slot_type"] == "break"
        assert data["lesson_type"] is None
        assert data["academic_equivalent_minutes"] == 0.0

    def test_create_lunch(self, client: TestClient):
        payload = {
            "name": "Almuerzo",
            "start_time": "11:20",
            "end_time": "12:20",
            "slot_type": "lunch",
            "lesson_type": None,
            "weekday": 0,
            "section": "day",
            "is_active": True,
        }
        resp = client.post("/api/time-slots/", json=payload)
        assert resp.status_code == 201
        assert resp.json()["academic_equivalent_minutes"] == 0.0

    def test_create_night_section(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(
                name="Bloque N1",
                start="18:00",
                end="19:00",
                lesson_type="technical",
                weekday=0,
                section="night",
            ),
        )
        assert resp.status_code == 201
        assert resp.json()["section"] == "night"


class TestValidation:
    def test_end_before_start_rejected(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(start="10:00", end="09:00"),
        )
        assert resp.status_code == 422

    def test_lesson_without_lesson_type_rejected(self, client: TestClient):
        payload = make_lesson()
        payload["lesson_type"] = None
        resp = client.post("/api/time-slots/", json=payload)
        assert resp.status_code == 422

    def test_break_with_lesson_type_rejected(self, client: TestClient):
        payload = make_break()
        payload["lesson_type"] = "academic"
        resp = client.post("/api/time-slots/", json=payload)
        assert resp.status_code == 422

    def test_overlap_same_weekday_section_rejected(self, client: TestClient):
        # Crear primer slot 07:00-07:40
        client.post("/api/time-slots/", json=make_lesson())
        # Intentar crear slot que solapa: 07:20-08:00
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(name="Bloque 2", start="07:20", end="08:00"),
        )
        assert resp.status_code == 409

    def test_overlap_different_section_allowed(self, client: TestClient):
        """Mismo horario en otra sección NO debe dar conflicto"""
        client.post("/api/time-slots/", json=make_lesson(section="day"))
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(section="night"),
        )
        assert resp.status_code == 201

    def test_overlap_different_weekday_allowed(self, client: TestClient):
        """Mismo horario en otro día NO debe dar conflicto"""
        client.post("/api/time-slots/", json=make_lesson(weekday=0))
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(weekday=1),
        )
        assert resp.status_code == 201

    def test_adjacent_slots_not_overlap(self, client: TestClient):
        """Slots contiguos (fin = inicio del siguiente) no deben solapar"""
        client.post("/api/time-slots/", json=make_lesson(start="07:00", end="07:40"))
        resp = client.post(
            "/api/time-slots/",
            json=make_lesson(name="Bloque 2", start="07:40", end="08:20"),
        )
        assert resp.status_code == 201


class TestReadTimeSlots:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/api/time-slots/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_created(self, client: TestClient):
        client.post("/api/time-slots/", json=make_lesson())
        resp = client.get("/api/time-slots/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_by_id(self, client: TestClient):
        created = client.post("/api/time-slots/", json=make_lesson()).json()
        resp = client.get(f"/api/time-slots/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_by_id_not_found(self, client: TestClient):
        resp = client.get("/api/time-slots/9999")
        assert resp.status_code == 404

    def test_filter_by_weekday(self, client: TestClient):
        client.post("/api/time-slots/", json=make_lesson(weekday=0))
        client.post(
            "/api/time-slots/",
            json=make_lesson(name="Bloque 2", weekday=1),
        )
        resp = client.get("/api/time-slots/?weekday=0")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["weekday"] == 0

    def test_filter_by_section(self, client: TestClient):
        client.post("/api/time-slots/", json=make_lesson(section="day"))
        client.post(
            "/api/time-slots/",
            json=make_lesson(name="Bloque N1", section="night"),
        )
        resp = client.get("/api/time-slots/?section=night")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["section"] == "night"

    def test_filter_by_slot_type(self, client: TestClient):
        client.post("/api/time-slots/", json=make_lesson())
        client.post("/api/time-slots/", json=make_break())
        resp = client.get("/api/time-slots/?slot_type=break")
        assert resp.status_code == 200
        data = resp.json()
        assert all(s["slot_type"] == "break" for s in data)

    def test_filter_by_is_active(self, client: TestClient):
        client.post("/api/time-slots/", json=make_lesson(is_active=True))
        client.post(
            "/api/time-slots/",
            json=make_lesson(name="Inactivo", start="07:40", end="08:20", is_active=False),
        )
        resp = client.get("/api/time-slots/?is_active=false")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["is_active"] is False


class TestUpdateTimeSlot:
    def test_update_name(self, client: TestClient):
        created = client.post("/api/time-slots/", json=make_lesson()).json()
        resp = client.put(
            f"/api/time-slots/{created['id']}",
            json={"name": "Bloque Actualizado"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bloque Actualizado"

    def test_update_not_found(self, client: TestClient):
        resp = client.put("/api/time-slots/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_update_causes_overlap_rejected(self, client: TestClient):
        a = client.post("/api/time-slots/", json=make_lesson(start="07:00", end="07:40")).json()
        b = client.post(
            "/api/time-slots/",
            json=make_lesson(name="Bloque 2", start="07:40", end="08:20"),
        ).json()
        # Intentar mover B para que solape con A
        resp = client.put(f"/api/time-slots/{b['id']}", json={"start_time": "07:20"})
        assert resp.status_code == 409

    def test_update_self_no_false_overlap(self, client: TestClient):
        """Actualizar un slot con sus mismos horarios no debe generar overlap consigo mismo"""
        created = client.post("/api/time-slots/", json=make_lesson()).json()
        resp = client.put(
            f"/api/time-slots/{created['id']}",
            json={"name": "Mismo horario, nuevo nombre"},
        )
        assert resp.status_code == 200


class TestDeleteTimeSlot:
    def test_delete_success(self, client: TestClient):
        created = client.post("/api/time-slots/", json=make_lesson()).json()
        resp = client.delete(f"/api/time-slots/{created['id']}")
        assert resp.status_code == 204
        # Verificar que ya no existe
        assert client.get(f"/api/time-slots/{created['id']}").status_code == 404

    def test_delete_not_found(self, client: TestClient):
        resp = client.delete("/api/time-slots/9999")
        assert resp.status_code == 404


# ─────────────────────────────────────────────
# Seed template
# ─────────────────────────────────────────────

class TestSeedTemplate:
    def test_seed_day_template_monday(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": False},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["created"] == 13
        assert data["skipped"] == 0
        assert data["overwritten"] == 0

    def test_seed_night_template_monday(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/seed-template",
            json={"section": "night", "weekdays": [0], "overwrite": False},
        )
        assert resp.status_code == 201
        assert resp.json()["created"] == 5

    def test_seed_multiple_weekdays(self, client: TestClient):
        resp = client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0, 1, 2, 3, 4], "overwrite": False},
        )
        assert resp.status_code == 201
        # 13 bloques × 5 días
        assert resp.json()["created"] == 65

    def test_seed_skips_existing_without_overwrite(self, client: TestClient):
        # Primera siembra
        client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": False},
        )
        # Segunda siembra sin overwrite → debe omitir
        resp = client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": False},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["created"] == 0
        assert data["skipped"] == 13

    def test_seed_overwrites_when_flag_true(self, client: TestClient):
        # Primera siembra
        client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": False},
        )
        # Segunda siembra con overwrite=True → recrea todo
        resp = client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": True},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["overwritten"] == 13
        assert data["created"] == 0

    def test_seed_creates_correct_slot_types(self, client: TestClient, db_session: Session):
        client.post(
            "/api/time-slots/seed-template",
            json={"section": "day", "weekdays": [0], "overwrite": False},
        )
        slots = db_session.query(TimeSlot).filter_by(weekday=0, section="day").all()
        types = {s.slot_type for s in slots}
        assert SlotType.LESSON in types
        assert SlotType.BREAK in types
        assert SlotType.LUNCH in types


# ─────────────────────────────────────────────
# Permisos
# ─────────────────────────────────────────────

class TestTimeSlotPermissions:
    def test_get_without_token_returns_401(self, real_client: TestClient):
        assert real_client.get("/api/time-slots/").status_code == 401

    def test_post_without_token_returns_401(self, real_client: TestClient):
        assert real_client.post("/api/time-slots/", json=make_lesson()).status_code == 401

    def test_put_without_token_returns_401(self, real_client: TestClient):
        assert real_client.put("/api/time-slots/1", json={"name": "X"}).status_code == 401

    def test_delete_without_token_returns_401(self, real_client: TestClient):
        assert real_client.delete("/api/time-slots/1").status_code == 401

    def test_seed_without_token_returns_401(self, real_client: TestClient):
        assert (
            real_client.post(
                "/api/time-slots/seed-template",
                json={"section": "day", "weekdays": [0]},
            ).status_code
            == 401
        )

    def test_teacher_can_get_time_slots(
        self, real_client: TestClient, teacher_headers: dict
    ):
        """Teachers (rol read-only) pueden listar time slots"""
        resp = real_client.get("/api/time-slots/", headers=teacher_headers)
        assert resp.status_code == 200

    def test_teacher_cannot_create_time_slot(
        self, real_client: TestClient, teacher_headers: dict
    ):
        """Teachers no pueden crear time slots (403)"""
        resp = real_client.post("/api/time-slots/", json=make_lesson(), headers=teacher_headers)
        assert resp.status_code == 403
