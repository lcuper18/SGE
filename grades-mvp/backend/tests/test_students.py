"""
Tests para Students API
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import Subgroup


def test_create_student(client: TestClient, db_session: Session):
    """Test crear estudiante"""
    # Crear estructura académica necesaria
    year = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    }).json()
    
    grade = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 1,
        "name": "Primer Grado"
    }).json()
    
    group = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 30
    }).json()
    
    # Crear subgrupo
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez García",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["identification"] == "EST001"
    assert data["first_name"] == "Juan"
    assert data["last_name"] == "Pérez García"
    assert data["full_name"] == "Juan Pérez García"
    assert data["is_active"] is True
    assert data["subgroup_id"] == subgroup.id


def test_create_student_duplicate_identification(client: TestClient, db_session: Session):
    """Test crear estudiante con identification duplicado debe fallar"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear primer estudiante
    client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    
    # Intentar crear otro con mismo identification
    response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "María",
        "last_name": "López",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup.id
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_student_with_nonexistent_subgroup(client: TestClient):
    """Test crear estudiante con subgroup inexistente debe fallar"""
    response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": 9999
    })
    
    assert response.status_code == 404
    assert "Subgroup 9999 not found" in response.json()["detail"]


def test_get_students_empty(client: TestClient):
    """Test obtener estudiantes cuando no hay ninguno"""
    response = client.get("/api/students/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["students"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["total_pages"] == 0


def test_get_students_with_pagination(client: TestClient, db_session: Session):
    """Test obtener estudiantes con paginación"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear 5 estudiantes
    for i in range(5):
        client.post("/api/students/", json={
            "identification": f"EST00{i+1}",
            "first_name": f"Estudiante{i+1}",
            "last_name": "Test",
            "date_of_birth": "2015-01-15",
            "subgroup_id": subgroup.id
        })
    
    # Obtener página 1 con page_size=2
    response = client.get("/api/students/?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["students"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3
    
    # Obtener página 2
    response = client.get("/api/students/?page=2&page_size=2")
    data = response.json()
    assert len(data["students"]) == 2
    assert data["page"] == 2


def test_search_students_by_identification(client: TestClient, db_session: Session):
    """Test buscar estudiantes por identification"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiantes
    client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    client.post("/api/students/", json={
        "identification": "EST002",
        "first_name": "María",
        "last_name": "García",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup.id
    })
    
    # Buscar por identification
    response = client.get("/api/students/?search=EST001")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["students"][0]["identification"] == "EST001"


def test_search_students_by_name(client: TestClient, db_session: Session):
    """Test buscar estudiantes por nombre"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiantes
    client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan Carlos",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    client.post("/api/students/", json={
        "identification": "EST002",
        "first_name": "María",
        "last_name": "García López",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup.id
    })
    
    # Buscar por primer nombre (case insensitive)
    response = client.get("/api/students/?search=juan")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Juan" in data["students"][0]["first_name"]
    
    # Buscar por apellido
    response = client.get("/api/students/?search=garcía")
    data = response.json()
    assert data["total"] == 1
    assert "García" in data["students"][0]["last_name"]


def test_filter_students_by_is_active(client: TestClient, db_session: Session):
    """Test filtrar estudiantes por estado activo/inactivo"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiantes
    student1_response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    student1_id = student1_response.json()["id"]
    
    client.post("/api/students/", json={
        "identification": "EST002",
        "first_name": "María",
        "last_name": "García",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup.id
    })
    
    # Desactivar primer estudiante
    client.delete(f"/api/students/{student1_id}")
    
    # Filtrar solo activos
    response = client.get("/api/students/?is_active=true")
    data = response.json()
    assert data["total"] == 1
    assert data["students"][0]["is_active"] is True
    
    # Filtrar solo inactivos
    response = client.get("/api/students/?is_active=false")
    data = response.json()
    assert data["total"] == 1
    assert data["students"][0]["is_active"] is False


def test_filter_students_by_subgroup(client: TestClient, db_session: Session):
    """Test filtrar estudiantes por subgrupo"""
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
    
    # Crear 2 subgrupos
    subgroup1 = Subgroup(group_id=group["id"], name="Subgrupo 1")
    subgroup2 = Subgroup(group_id=group["id"], name="Subgrupo 2")
    db_session.add_all([subgroup1, subgroup2])
    db_session.commit()
    db_session.refresh(subgroup1)
    db_session.refresh(subgroup2)
    
    # Crear estudiantes en diferentes subgrupos
    client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup1.id
    })
    client.post("/api/students/", json={
        "identification": "EST002",
        "first_name": "María",
        "last_name": "García",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup2.id
    })
    client.post("/api/students/", json={
        "identification": "EST003",
        "first_name": "Carlos",
        "last_name": "López",
        "date_of_birth": "2015-03-10",
        "subgroup_id": subgroup1.id
    })
    
    # Filtrar por subgroup1
    response = client.get(f"/api/students/?subgroup_id={subgroup1.id}")
    data = response.json()
    assert data["total"] == 2
    
    # Filtrar por subgroup2
    response = client.get(f"/api/students/?subgroup_id={subgroup2.id}")
    data = response.json()
    assert data["total"] == 1


def test_get_student_by_id(client: TestClient, db_session: Session):
    """Test obtener estudiante por ID"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    create_response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    student_id = create_response.json()["id"]
    
    # Obtener por ID
    response = client.get(f"/api/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id
    assert data["identification"] == "EST001"


def test_get_nonexistent_student(client: TestClient):
    """Test obtener estudiante inexistente debe fallar"""
    response = client.get("/api/students/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_student(client: TestClient, db_session: Session):
    """Test actualizar estudiante"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    create_response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    student_id = create_response.json()["id"]
    
    # Actualizar
    response = client.put(f"/api/students/{student_id}", json={
        "first_name": "Juan Carlos",
        "last_name": "Pérez García"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Juan Carlos"
    assert data["last_name"] == "Pérez García"
    assert data["identification"] == "EST001"  # No cambió


def test_update_student_duplicate_identification(client: TestClient, db_session: Session):
    """Test actualizar estudiante con identification duplicado debe fallar"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear dos estudiantes
    client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    
    create_response2 = client.post("/api/students/", json={
        "identification": "EST002",
        "first_name": "María",
        "last_name": "García",
        "date_of_birth": "2015-02-20",
        "subgroup_id": subgroup.id
    })
    student2_id = create_response2.json()["id"]
    
    # Intentar cambiar identification de EST002 a EST001 (que ya existe)
    response = client.put(f"/api/students/{student2_id}", json={
        "identification": "EST001"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_student_with_invalid_subgroup(client: TestClient, db_session: Session):
    """Test actualizar estudiante con subgroup inválido debe fallar"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    create_response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    student_id = create_response.json()["id"]
    
    # Intentar cambiar a subgroup inexistente
    response = client.put(f"/api/students/{student_id}", json={
        "subgroup_id": 9999
    })
    
    assert response.status_code == 404
    assert "Subgroup 9999 not found" in response.json()["detail"]


def test_soft_delete_student(client: TestClient, db_session: Session):
    """Test soft delete de estudiante"""
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
    subgroup = Subgroup(group_id=group["id"], name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    create_response = client.post("/api/students/", json={
        "identification": "EST001",
        "first_name": "Juan",
        "last_name": "Pérez",
        "date_of_birth": "2015-01-15",
        "subgroup_id": subgroup.id
    })
    student_id = create_response.json()["id"]
    
    # Verificar que está activo
    response = client.get(f"/api/students/{student_id}")
    assert response.json()["is_active"] is True
    
    # Soft delete
    response = client.delete(f"/api/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    
    # Verificar que sigue existiendo pero inactivo
    response = client.get(f"/api/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["is_active"] is False
