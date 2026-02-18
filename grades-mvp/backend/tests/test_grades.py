"""
Tests para Grades API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import Group


def test_create_grade(client: TestClient, db_session: Session):
    """Test crear grado/nivel educativo"""
    # Crear año académico primero
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear grado
    response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado",
        "description": "Primer grado de primaria"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["level"] == 1
    assert data["name"] == "Primer Grado"
    assert data["description"] == "Primer grado de primaria"
    assert data["academic_year_id"] == year_id
    assert "id" in data


def test_create_grade_without_description(client: TestClient, db_session: Session):
    """Test crear grado sin descripción (campo opcional)"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear grado sin descripción
    response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 2,
        "name": "Segundo Grado"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["level"] == 2
    assert data["description"] is None


def test_create_duplicate_grade_level(client: TestClient, db_session: Session):
    """Test crear grado con level duplicado en mismo año debe fallar"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear primer grado
    client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado A"
    })
    
    # Intentar crear otro grado con el mismo level
    response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado B"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_grade_same_level_different_years(client: TestClient, db_session: Session):
    """Test crear grado con mismo level en diferentes años debe funcionar"""
    # Crear dos años académicos
    year1 = client.post("/api/academic-years/", json={
        "year": 2025,
        "name": "Año 2025",
        "is_active": False
    }).json()
    
    year2 = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    }).json()
    
    # Crear grado level 1 en año 2025
    response1 = client.post("/api/grades/", json={
        "academic_year_id": year1["id"],
        "level": 1,
        "name": "Primer Grado 2025"
    })
    
    # Crear grado level 1 en año 2026 (debe funcionar)
    response2 = client.post("/api/grades/", json={
        "academic_year_id": year2["id"],
        "level": 1,
        "name": "Primer Grado 2026"
    })
    
    assert response1.status_code == 201
    assert response2.status_code == 201


def test_create_grade_with_nonexistent_academic_year(client: TestClient, db_session: Session):
    """Test crear grado con año académico inexistente"""
    response = client.post("/api/grades/", json={
        "academic_year_id": 9999,
        "level": 1,
        "name": "Primer Grado"
    })
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_grade_with_invalid_level(client: TestClient, db_session: Session):
    """Test crear grado con level fuera de rango"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Intentar crear grado con level 0 (inválido)
    response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 0,
        "name": "Nivel Inválido"
    })
    
    assert response.status_code == 422  # Validation error


def test_get_all_grades(client: TestClient, db_session: Session):
    """Test obtener todos los grados"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear varios grados
    client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 3,
        "name": "Tercer Grado"
    })
    client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 2,
        "name": "Segundo Grado"
    })
    
    response = client.get("/api/grades/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Verificar orden por level
    assert data[0]["level"] == 1
    assert data[1]["level"] == 2
    assert data[2]["level"] == 3


def test_get_grades_filtered_by_academic_year(client: TestClient, db_session: Session):
    """Test obtener grados filtrados por año académico"""
    # Crear dos años académicos
    year1 = client.post("/api/academic-years/", json={
        "year": 2025,
        "name": "Año 2025",
        "is_active": False
    }).json()
    
    year2 = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    }).json()
    
    # Crear grados para cada año
    client.post("/api/grades/", json={
        "academic_year_id": year1["id"],
        "level": 1,
        "name": "Primer Grado 2025"
    })
    client.post("/api/grades/", json={
        "academic_year_id": year2["id"],
        "level": 1,
        "name": "Primer Grado 2026"
    })
    client.post("/api/grades/", json={
        "academic_year_id": year2["id"],
        "level": 2,
        "name": "Segundo Grado 2026"
    })
    
    # Filtrar grados del año 2026
    response = client.get(f"/api/grades/?academic_year_id={year2['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(g["academic_year_id"] == year2["id"] for g in data)


def test_get_grade_by_id(client: TestClient, db_session: Session):
    """Test obtener grado por ID"""
    # Crear año y grado
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    grade_response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    grade_id = grade_response.json()["id"]
    
    # Obtener por ID
    response = client.get(f"/api/grades/{grade_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == grade_id
    assert data["name"] == "Primer Grado"


def test_get_nonexistent_grade(client: TestClient, db_session: Session):
    """Test obtener grado inexistente"""
    response = client.get("/api/grades/9999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_grade(client: TestClient, db_session: Session):
    """Test actualizar grado"""
    # Crear año y grado
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    grade_response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    grade_id = grade_response.json()["id"]
    
    # Actualizar
    response = client.put(f"/api/grades/{grade_id}", json={
        "name": "Primer Grado - Actualizado",
        "description": "Nueva descripción"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Primer Grado - Actualizado"
    assert data["description"] == "Nueva descripción"
    assert data["level"] == 1  # No cambió


def test_update_grade_level_to_existing(client: TestClient, db_session: Session):
    """Test actualizar level a uno que ya existe debe fallar"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear dos grados
    client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    
    grade2_response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 2,
        "name": "Segundo Grado"
    })
    grade2_id = grade2_response.json()["id"]
    
    # Intentar actualizar grade2 al level 1 (que ya existe)
    response = client.put(f"/api/grades/{grade2_id}", json={
        "level": 1
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_delete_grade(client: TestClient, db_session: Session):
    """Test eliminar grado sin grupos asociados"""
    # Crear año y grado
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    grade_response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    grade_id = grade_response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/api/grades/{grade_id}")
    
    assert response.status_code == 204
    
    # Verificar que no existe
    response = client.get(f"/api/grades/{grade_id}")
    assert response.status_code == 404


def test_delete_grade_with_groups(client: TestClient, db_session: Session):
    """Test eliminar grado con grupos asociados debe fallar"""
    # Crear año y grado
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    grade_response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 1,
        "name": "Primer Grado"
    })
    grade_id = grade_response.json()["id"]
    
    # Crear un grupo asociado manualmente en la DB
    from app.models.academic import Grade
    grade = db_session.query(Grade).filter(Grade.id == grade_id).first()
    
    # Crear grupo asociado
    group = Group(
        grade_id=grade_id,
        name="Grupo A",
        capacity=30
    )
    db_session.add(group)
    db_session.commit()
    
    # Intentar eliminar grado con grupos
    response = client.delete(f"/api/grades/{grade_id}")
    
    assert response.status_code == 400
    assert "Cannot delete" in response.json()["detail"]


def test_create_grade_with_level_7(client: TestClient, db_session: Session):
    """Test crear grado con level 7 (fuera de rango 1-6)"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Intentar crear grado con level 7
    response = client.post("/api/grades/", json={
        "academic_year_id": year_id,
        "level": 7,
        "name": "Séptimo Grado"
    })
    
    assert response.status_code == 422  # Validation error
