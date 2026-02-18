"""
Tests para Periods API
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_period(client: TestClient, db_session: Session):
    """Test crear período académico"""
    # Crear año académico primero
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear período
    response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": True
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Primer Trimestre"
    assert data["academic_year_id"] == year_id
    assert data["is_active"] is True
    assert "id" in data


def test_create_period_with_invalid_dates(client: TestClient, db_session: Session):
    """Test crear período con end_date anterior a start_date"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Intentar crear período con fechas inválidas
    response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Período Inválido",
        "start_date": "2026-05-31",
        "end_date": "2026-02-01",  # Anterior a start_date
        "is_active": False
    })
    
    assert response.status_code == 422  # Validation error


def test_create_period_with_overlapping_dates(client: TestClient, db_session: Session):
    """Test crear período con fechas solapadas debe fallar"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear primer período
    client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    
    # Intentar crear segundo período con fechas solapadas
    response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Período Solapado",
        "start_date": "2026-05-01",  # Solapa con el primero
        "end_date": "2026-08-31",
        "is_active": False
    })
    
    assert response.status_code == 400
    assert "overlap" in response.json()["detail"].lower()


def test_create_period_with_nonexistent_academic_year(client: TestClient, db_session: Session):
    """Test crear período con año académico inexistente"""
    response = client.post("/api/periods/", json={
        "academic_year_id": 9999,
        "name": "Período Inválido",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_all_periods(client: TestClient, db_session: Session):
    """Test obtener todos los períodos"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear varios períodos
    client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Segundo Trimestre",
        "start_date": "2026-06-01",
        "end_date": "2026-09-30",
        "is_active": False
    })
    
    response = client.get("/api/periods/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verificar orden por fecha de inicio
    assert data[0]["name"] == "Primer Trimestre"
    assert data[1]["name"] == "Segundo Trimestre"


def test_get_periods_filtered_by_academic_year(client: TestClient, db_session: Session):
    """Test obtener períodos filtrados por año académico"""
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
    
    # Crear períodos para cada año
    client.post("/api/periods/", json={
        "academic_year_id": year1["id"],
        "name": "Período 2025",
        "start_date": "2025-02-01",
        "end_date": "2025-05-31",
        "is_active": False
    })
    client.post("/api/periods/", json={
        "academic_year_id": year2["id"],
        "name": "Período 2026",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    
    # Filtrar períodos del año 2026
    response = client.get(f"/api/periods/?academic_year_id={year2['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Período 2026"


def test_get_period_by_id(client: TestClient, db_session: Session):
    """Test obtener período por ID"""
    # Crear año y período
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    period_response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": True
    })
    period_id = period_response.json()["id"]
    
    # Obtener por ID
    response = client.get(f"/api/periods/{period_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == period_id
    assert data["name"] == "Primer Trimestre"


def test_get_nonexistent_period(client: TestClient, db_session: Session):
    """Test obtener período inexistente"""
    response = client.get("/api/periods/9999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_period(client: TestClient, db_session: Session):
    """Test actualizar período"""
    # Crear año y período
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    period_response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    period_id = period_response.json()["id"]
    
    # Actualizar
    response = client.put(f"/api/periods/{period_id}", json={
        "name": "Primer Período - Actualizado",
        "is_active": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Primer Período - Actualizado"
    assert data["is_active"] is True


def test_only_one_active_period_per_year(client: TestClient, db_session: Session):
    """Test que solo un período puede estar activo por año académico"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear primer período activo
    period1_response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": True
    })
    period1_id = period1_response.json()["id"]
    
    # Crear segundo período activo
    client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Segundo Trimestre",
        "start_date": "2026-06-01",
        "end_date": "2026-09-30",
        "is_active": True
    })
    
    # Verificar que el primero se desactivó
    response = client.get(f"/api/periods/{period1_id}")
    assert response.json()["is_active"] is False


def test_delete_period(client: TestClient, db_session: Session):
    """Test eliminar período"""
    # Crear año y período
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    period_response = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    })
    period_id = period_response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/api/periods/{period_id}")
    
    assert response.status_code == 204
    
    # Verificar que no existe
    response = client.get(f"/api/periods/{period_id}")
    assert response.status_code == 404


def test_update_period_with_overlapping_dates(client: TestClient, db_session: Session):
    """Test actualizar período con fechas que solapen con otro debe fallar"""
    # Crear año académico
    year_response = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    })
    year_id = year_response.json()["id"]
    
    # Crear dos períodos sin solapamiento
    period1 = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Primer Trimestre",
        "start_date": "2026-02-01",
        "end_date": "2026-05-31",
        "is_active": False
    }).json()
    
    period2 = client.post("/api/periods/", json={
        "academic_year_id": year_id,
        "name": "Segundo Trimestre",
        "start_date": "2026-06-01",
        "end_date": "2026-09-30",
        "is_active": False
    }).json()
    
    # Intentar actualizar period2 para que solape con period1
    response = client.put(f"/api/periods/{period2['id']}", json={
        "start_date": "2026-05-01"  # Solapa con period1
    })
    
    assert response.status_code == 400
    assert "overlap" in response.json()["detail"].lower()
