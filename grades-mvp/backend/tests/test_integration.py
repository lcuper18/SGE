"""
Integration Tests - End-to-end workflows
Tests que validan flujos completos del sistema académico
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import AcademicYear, Grade, Group, Subgroup
from app.models.student import Student


def test_full_academic_structure_flow(client: TestClient, db_session: Session):
    """
    Test de integración: Flujo completo
    year → period → grade → group → subgroup → student
    """
    # 1. Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año Académico 2026",
        "is_active": True
    })
    assert year_response.status_code == 201
    year = year_response.json()
    
    # 2. Crear período
    start_date = date.today()
    end_date = start_date + timedelta(days=90)
    period_response = client.post("/api/periods/", json={
        "academic_year_id": year["id"],
        "name": "Primer Trimestre",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "is_active": True
    })
    assert period_response.status_code == 201
    period = period_response.json()
    
    # 3. Crear grado
    grade_response = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 1,
        "name": "Primer Grado",
        "description": "Primer nivel de educación primaria"
    })
    assert grade_response.status_code == 201
    grade = grade_response.json()
    
    # 4. Crear grupo
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 25
    })
    assert group_response.status_code == 201
    group = group_response.json()
    
    # 5. Crear subgrupo manualmente (vía DB)
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # 6. Crear estudiante
    student_response = client.post("/api/students/", json={
        "identification": "EST2026001",
        "first_name": "Ana María",
        "last_name": "González Castro",
        "date_of_birth": "2018-03-15",
        "subgroup_id": subgroup.id
    })
    assert student_response.status_code == 201
    student = student_response.json()
    
    # Verificaciones de integridad
    assert student["subgroup_id"] == subgroup.id
    assert group["student_count"] == 0  # Contador inicial
    
    # Verificar que el estudiante aparece en el grupo
    group_students = client.get(f"/api/groups/{group['id']}/students/")
    assert group_students.status_code == 200
    students_list = group_students.json()
    assert len(students_list) == 1
    assert students_list[0]["identification"] == "EST2026001"
    
    # Verificar que el contador se actualiza
    updated_group = client.get(f"/api/groups/{group['id']}")
    assert updated_group.json()["student_count"] == 1


def test_multiple_students_assignment_to_groups(client: TestClient, db_session: Session):
    """
    Test de integración: Asignar múltiples estudiantes a grupos
    Verifica que los estudiantes se distribuyen correctamente
    """
    # Crear estructura académica
    year = client.post("/api/academic-years/", json={
        "year": 2026, "name": "Año 2026", "is_active": True
    }).json()
    
    grade = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 2,
        "name": "Segundo Grado"
    }).json()
    
    # Crear 3 grupos
    group_a = client.post("/api/groups/", json={
        "grade_id": grade["id"], "name": "Sección A", "capacity": 10
    }).json()
    
    group_b = client.post("/api/groups/", json={
        "grade_id": grade["id"], "name": "Sección B", "capacity": 10
    }).json()
    
    group_c = client.post("/api/groups/", json={
        "grade_id": grade["id"], "name": "Sección C", "capacity": 10
    }).json()
    
    # Crear subgrupos para cada grupo
    subgroup_a = Subgroup(group_id=group_a["id"], name="Subgrupo A1")
    subgroup_b = Subgroup(group_id=group_b["id"], name="Subgrupo B1")
    subgroup_c = Subgroup(group_id=group_c["id"], name="Subgrupo C1")
    db_session.add_all([subgroup_a, subgroup_b, subgroup_c])
    db_session.commit()
    db_session.refresh(subgroup_a)
    db_session.refresh(subgroup_b)
    db_session.refresh(subgroup_c)
    
    # Asignar estudiantes a diferentes grupos
    students_data = [
        ("EST001", "Juan", "Pérez", subgroup_a.id),
        ("EST002", "María", "García", subgroup_a.id),
        ("EST003", "Carlos", "López", subgroup_b.id),
        ("EST004", "Ana", "Martínez", subgroup_b.id),
        ("EST005", "Luis", "Rodríguez", subgroup_c.id),
    ]
    
    for identification, first_name, last_name, subgroup_id in students_data:
        response = client.post("/api/students/", json={
            "identification": identification,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": "2016-01-01",
            "subgroup_id": subgroup_id
        })
        assert response.status_code == 201
    
    # Verificar distribución
    group_a_students = client.get(f"/api/groups/{group_a['id']}/students/").json()
    assert len(group_a_students) == 2
    
    group_b_students = client.get(f"/api/groups/{group_b['id']}/students/").json()
    assert len(group_b_students) == 2
    
    group_c_students = client.get(f"/api/groups/{group_c['id']}/students/").json()
    assert len(group_c_students) == 1
    
    # Verificar student_count
    assert client.get(f"/api/groups/{group_a['id']}").json()["student_count"] == 2
    assert client.get(f"/api/groups/{group_b['id']}").json()["student_count"] == 2
    assert client.get(f"/api/groups/{group_c['id']}").json()["student_count"] == 1


def test_group_capacity_validation(client: TestClient, db_session: Session):
    """
    Test de integración: Validar que no se puede reducir capacidad
    por debajo del número de estudiantes asignados
    """
    # Crear estructura
    year = client.post("/api/academic-years/", json={
        "year": 2026, "name": "Año 2026", "is_active": True
    }).json()
    
    grade = client.post("/api/grades/", json={
        "academic_year_id": year["id"], "level": 1, "name": "Primer Grado"
    }).json()
    
    group = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 20
    }).json()
    
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Asignar 8 estudiantes
    for i in range(8):
        client.post("/api/students/", json={
            "identification": f"EST00{i+1}",
            "first_name": f"Estudiante{i+1}",
            "last_name": "Test",
            "date_of_birth": "2016-01-01",
            "subgroup_id": subgroup.id
        })
    
    # Verificar que hay 8 estudiantes
    assert client.get(f"/api/groups/{group['id']}").json()["student_count"] == 8
    
    # Intentar reducir capacidad a 5 (debe fallar)
    response = client.put(f"/api/groups/{group['id']}", json={
        "capacity": 5
    })
    assert response.status_code == 400
    assert "Cannot set capacity" in response.json()["detail"]
    assert "8 students" in response.json()["detail"]
    
    # Reducir capacidad a 10 (debe funcionar)
    response = client.put(f"/api/groups/{group['id']}", json={
        "capacity": 10
    })
    assert response.status_code == 200
    assert response.json()["capacity"] == 10


def test_academic_year_filters_cascade(client: TestClient, db_session: Session):
    """
    Test de integración: Verificar que los filtros por año académico
    funcionan correctamente en toda la jerarquía
    """
    # Crear 2 años académicos
    year_2025 = client.post("/api/academic-years/", json={
        "year": 2025, "name": "Año 2025", "is_active": False
    }).json()
    
    year_2026 = client.post("/api/academic-years/", json={
        "year": 2026, "name": "Año 2026", "is_active": True
    }).json()
    
    # Crear grados en cada año
    grade_2025_1 = client.post("/api/grades/", json={
        "academic_year_id": year_2025["id"], "level": 1, "name": "Primer Grado 2025"
    }).json()
    
    grade_2026_1 = client.post("/api/grades/", json={
        "academic_year_id": year_2026["id"], "level": 1, "name": "Primer Grado 2026"
    }).json()
    
    grade_2026_2 = client.post("/api/grades/", json={
        "academic_year_id": year_2026["id"], "level": 2, "name": "Segundo Grado 2026"
    }).json()
    
    # Crear grupos en cada grado
    group_2025 = client.post("/api/groups/", json={
        "grade_id": grade_2025_1["id"], "name": "Sección A"
    }).json()
    
    group_2026_1 = client.post("/api/groups/", json={
        "grade_id": grade_2026_1["id"], "name": "Sección A"
    }).json()
    
    group_2026_2 = client.post("/api/groups/", json={
        "grade_id": grade_2026_2["id"], "name": "Sección B"
    }).json()
    
    # Filtrar grados por año académico
    grades_2025 = client.get(f"/api/grades/?academic_year_id={year_2025['id']}").json()
    assert len(grades_2025) == 1
    assert grades_2025[0]["level"] == 1
    
    grades_2026 = client.get(f"/api/grades/?academic_year_id={year_2026['id']}").json()
    assert len(grades_2026) == 2
    
    # Filtrar grupos por año académico
    groups_2025 = client.get(f"/api/groups/?academic_year_id={year_2025['id']}").json()
    assert len(groups_2025) == 1
    assert groups_2025[0]["id"] == group_2025["id"]
    
    groups_2026 = client.get(f"/api/groups/?academic_year_id={year_2026['id']}").json()
    assert len(groups_2026) == 2
    groups_ids = [g["id"] for g in groups_2026]
    assert group_2026_1["id"] in groups_ids
    assert group_2026_2["id"] in groups_ids


def test_student_search_and_filters_integration(client: TestClient, db_session: Session):
    """
    Test de integración: Búsqueda y filtros de estudiantes
    combinados con paginación
    """
    # Crear estructura
    year = client.post("/api/academic-years/", json={
        "year": 2026, "name": "Año 2026", "is_active": True
    }).json()
    
    grade = client.post("/api/grades/", json={
        "academic_year_id": year["id"], "level": 1, "name": "Primer Grado"
    }).json()
    
    group = client.post("/api/groups/", json={
        "grade_id": grade["id"], "name": "Sección A"
    }).json()
    
    subgroup1 = Subgroup(group_id=group["id"], name="Subgrupo 1")
    subgroup2 = Subgroup(group_id=group["id"], name="Subgrupo 2")
    db_session.add_all([subgroup1, subgroup2])
    db_session.commit()
    db_session.refresh(subgroup1)
    db_session.refresh(subgroup2)
    
    # Crear 15 estudiantes con nombres variados
    students_data = [
        ("EST001", "Juan", "García", subgroup1.id),
        ("EST002", "María", "López", subgroup1.id),
        ("EST003", "Carlos", "García", subgroup2.id),
        ("EST004", "Ana", "Martínez", subgroup1.id),
        ("EST005", "Luis", "García", subgroup2.id),
        ("EST006", "Elena", "Rodríguez", subgroup1.id),
        ("EST007", "Pedro", "Sánchez", subgroup2.id),
        ("EST008", "Laura", "García", subgroup1.id),
        ("EST009", "Miguel", "Torres", subgroup2.id),
        ("EST010", "Sofia", "Ramírez", subgroup1.id),
        ("EST011", "Diego", "García", subgroup2.id),
        ("EST012", "Isabel", "Flores", subgroup1.id),
        ("EST013", "Roberto", "Cruz", subgroup2.id),
        ("EST014", "Carmen", "García", subgroup1.id),
        ("EST015", "Fernando", "Díaz", subgroup2.id),
    ]
    
    created_students = []
    for identification, first_name, last_name, subgroup_id in students_data:
        response = client.post("/api/students/", json={
            "identification": identification,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": "2016-01-01",
            "subgroup_id": subgroup_id
        })
        created_students.append(response.json())
    
    # Test 1: Buscar por apellido "García"
    response = client.get("/api/students/?search=garcía")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6  # 6 estudiantes con apellido García
    
    # Test 2: Filtrar por subgroup1
    response = client.get(f"/api/students/?subgroup_id={subgroup1.id}")
    data = response.json()
    assert data["total"] == 8  # 8 estudiantes en subgroup1
    
    # Test 3: Búsqueda + filtro combinado
    response = client.get(f"/api/students/?search=garcía&subgroup_id={subgroup1.id}")
    data = response.json()
    assert data["total"] == 3  # 3 García en subgroup1
    
    # Test 4: Paginación
    response = client.get("/api/students/?page=1&page_size=5")
    data = response.json()
    assert len(data["students"]) == 5
    assert data["total"] == 15
    assert data["total_pages"] == 3
    
    # Test 5: Desactivar algunos estudiantes
    for student_id in [created_students[0]["id"], created_students[1]["id"]]:
        client.delete(f"/api/students/{student_id}")
    
    # Filtrar solo activos
    response = client.get("/api/students/?is_active=true")
    data = response.json()
    assert data["total"] == 13
    
    # Filtrar solo inactivos
    response = client.get("/api/students/?is_active=false")
    data = response.json()
    assert data["total"] == 2
