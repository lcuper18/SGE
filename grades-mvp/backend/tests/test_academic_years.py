"""
Tests para Academic Years API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import AcademicYear


def test_create_academic_year(client: TestClient, db_session: Session):
    """Test crear año académico"""
    response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año Académico 2026",
        "is_active": True
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["year"] == 2026
    assert data["name"] == "Año Académico 2026"
    assert data["is_active"] is True
    assert "id" in data


def test_create_duplicate_year(client: TestClient, db_session: Session):
    """Test crear año académico duplicado debe fallar"""
    # Crear primero
    client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": False
    })
    
    # Intentar duplicar
    response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026 Duplicado",
        "is_active": False
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_all_academic_years(client: TestClient, db_session: Session):
    """Test obtener todos los años académicos"""
    # Crear varios años
    client.post("/api/academic-years/", json={"year": 2024, "name": "2024", "is_active": False})
    client.post("/api/academic-years/", json={"year": 2025, "name": "2025", "is_active": False})
    client.post("/api/academic-years/", json={"year": 2026, "name": "2026", "is_active": True})
    
    response = client.get("/api/academic-years/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Verificar orden descendente por año
    assert data[0]["year"] == 2026
    assert data[1]["year"] == 2025
    assert data[2]["year"] == 2024


def test_get_academic_year_by_id(client: TestClient, db_session: Session):
    """Test obtener año académico por ID"""
    # Crear año
    response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = response.json()["id"]
    
    # Obtener por ID
    response = client.get(f"/api/academic-years/{year_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == year_id
    assert data["year"] == 2026


def test_get_nonexistent_academic_year(client: TestClient, db_session: Session):
    """Test obtener año académico inexistente"""
    response = client.get("/api/academic-years/9999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_academic_year(client: TestClient, db_session: Session):
    """Test actualizar año académico"""
    # Crear año
    response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": False
    })
    year_id = response.json()["id"]
    
    # Actualizar
    response = client.put(f"/api/academic-years/{year_id}", json={
        "name": "Año Académico 2026 - Actualizado",
        "is_active": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Año Académico 2026 - Actualizado"
    assert data["is_active"] is True
    assert data["year"] == 2026  # No cambió


def test_only_one_active_year(client: TestClient, db_session: Session):
    """Test que solo un año puede estar activo a la vez"""
    # Crear primer año activo
    response1 = client.post("/api/academic-years/", json={
        "year": 2025,
        "name": "Año 2025",
        "is_active": True
    })
    year_id_1 = response1.json()["id"]
    
    # Crear segundo año activo
    client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    
    # Verificar que el primero se desactivó
    response = client.get(f"/api/academic-years/{year_id_1}")
    assert response.json()["is_active"] is False


def test_delete_academic_year(client: TestClient, db_session: Session):
    """Test eliminar año académico"""
    # Crear año
    response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": False
    })
    year_id = response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/api/academic-years/{year_id}")
    
    assert response.status_code == 204
    
    # Verificar que no existe
    response = client.get(f"/api/academic-years/{year_id}")
    assert response.status_code == 404


def test_create_academic_year_with_invalid_year(client: TestClient, db_session: Session):
    """Test crear año académico con año inválido"""
    response = client.post("/api/academic-years/", json={
        "year": 1999,  # Año fuera de rango (< 2020)
        "name": "Año 1999",
        "is_active": False
    })
    
    assert response.status_code == 422  # Validation error


def test_update_year_to_existing(client: TestClient, db_session: Session):
    """Test actualizar año a uno que ya existe debe fallar"""
    # Crear dos años
    client.post("/api/academic-years/", json={"year": 2025, "name": "2025", "is_active": False})
    response = client.post("/api/academic-years/", json={"year": 2026, "name": "2026", "is_active": False})
    year_id = response.json()["id"]
    
    # Intentar actualizar 2026 a 2025 (que ya existe)
    response = client.put(f"/api/academic-years/{year_id}", json={"year": 2025})
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
