"""
Tests para Groups API
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.academic import Subgroup
from app.models.student import Student


def test_create_group(client: TestClient, db_session: Session):
    """Test crear grupo"""
    # Crear año y grado
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
    
    # Crear grupo
    response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 30
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sección A"
    assert data["grade_id"] == grade["id"]
    assert data["capacity"] == 30
    assert data["student_count"] == 0
    assert "id" in data


def test_create_group_without_capacity(client: TestClient, db_session: Session):
    """Test crear grupo sin capacidad (campo opcional)"""
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
    
    # Crear grupo sin capacidad
    response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección B"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["capacity"] is None


def test_create_duplicate_group_name(client: TestClient, db_session: Session):
    """Test crear grupo con nombre duplicado en mismo grado debe fallar"""
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
    
    # Crear primer grupo
    client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    
    # Intentar crear grupo con mismo nombre
    response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_group_same_name_different_grades(client: TestClient, db_session: Session):
    """Test crear grupo con mismo nombre en diferentes grados debe funcionar"""
    year = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    }).json()
    
    grade1 = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 1,
        "name": "Primer Grado"
    }).json()
    
    grade2 = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 2,
        "name": "Segundo Grado"
    }).json()
    
    # Crear grupo "Sección A" en grado 1
    response1 = client.post("/api/groups/", json={
        "grade_id": grade1["id"],
        "name": "Sección A"
    })
    
    # Crear grupo "Sección A" en grado 2 (debe funcionar)
    response2 = client.post("/api/groups/", json={
        "grade_id": grade2["id"],
        "name": "Sección A"
    })
    
    assert response1.status_code == 201
    assert response2.status_code == 201


def test_create_group_with_nonexistent_grade(client: TestClient, db_session: Session):
    """Test crear grupo con grado inexistente"""
    response = client.post("/api/groups/", json={
        "grade_id": 9999,
        "name": "Sección A"
    })
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_all_groups(client: TestClient, db_session: Session):
    """Test obtener todos los grupos"""
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
    
    # Crear varios grupos
    client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección C"
    })
    client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección B"
    })
    
    response = client.get("/api/groups/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Verificar orden alfabético
    assert data[0]["name"] == "Sección A"
    assert data[1]["name"] == "Sección B"
    assert data[2]["name"] == "Sección C"


def test_get_groups_filtered_by_grade(client: TestClient, db_session: Session):
    """Test obtener grupos filtrados por grado"""
    year = client.post("/api/academic-years/", json={
        "year": 2026,
        "name": "Año 2026",
        "is_active": True
    }).json()
    
    grade1 = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 1,
        "name": "Primer Grado"
    }).json()
    
    grade2 = client.post("/api/grades/", json={
        "academic_year_id": year["id"],
        "level": 2,
        "name": "Segundo Grado"
    }).json()
    
    # Crear grupos para cada grado
    client.post("/api/groups/", json={
        "grade_id": grade1["id"],
        "name": "Grupo 1A"
    })
    client.post("/api/groups/", json={
        "grade_id": grade2["id"],
        "name": "Grupo 2A"
    })
    client.post("/api/groups/", json={
        "grade_id": grade2["id"],
        "name": "Grupo 2B"
    })
    
    # Filtrar grupos del grado 2
    response = client.get(f"/api/groups/?grade_id={grade2['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(g["grade_id"] == grade2["id"] for g in data)


def test_get_groups_filtered_by_academic_year(client: TestClient, db_session: Session):
    """Test obtener grupos filtrados por año académico"""
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
    
    grade1 = client.post("/api/grades/", json={
        "academic_year_id": year1["id"],
        "level": 1,
        "name": "Primer Grado 2025"
    }).json()
    
    grade2 = client.post("/api/grades/", json={
        "academic_year_id": year2["id"],
        "level": 1,
        "name": "Primer Grado 2026"
    }).json()
    
    # Crear grupos
    client.post("/api/groups/", json={
        "grade_id": grade1["id"],
        "name": "Grupo A"
    })
    client.post("/api/groups/", json={
        "grade_id": grade2["id"],
        "name": "Grupo A"
    })
    
    # Filtrar por año 2026
    response = client.get(f"/api/groups/?academic_year_id={year2['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["grade_id"] == grade2["id"]


def test_get_group_by_id(client: TestClient, db_session: Session):
    """Test obtener grupo por ID"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 25
    })
    group_id = group_response.json()["id"]
    
    # Obtener por ID
    response = client.get(f"/api/groups/{group_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == group_id
    assert data["name"] == "Sección A"
    assert data["capacity"] == 25
    assert data["student_count"] == 0


def test_get_nonexistent_group(client: TestClient, db_session: Session):
    """Test obtener grupo inexistente"""
    response = client.get("/api/groups/9999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_group(client: TestClient, db_session: Session):
    """Test actualizar grupo"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    group_id = group_response.json()["id"]
    
    # Actualizar
    response = client.put(f"/api/groups/{group_id}", json={
        "name": "Sección A - Actualizada",
        "capacity": 35
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sección A - Actualizada"
    assert data["capacity"] == 35


def test_update_group_name_to_existing(client: TestClient, db_session: Session):
    """Test actualizar nombre a uno que ya existe debe fallar"""
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
    
    # Crear dos grupos
    client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    
    group2 = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección B"
    }).json()
    
    # Intentar cambiar nombre a uno existente
    response = client.put(f"/api/groups/{group2['id']}", json={
        "name": "Sección A"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_delete_group(client: TestClient, db_session: Session):
    """Test eliminar grupo sin estudiantes"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    group_id = group_response.json()["id"]
    
    # Eliminar
    response = client.delete(f"/api/groups/{group_id}")
    
    assert response.status_code == 204
    
    # Verificar que no existe
    response = client.get(f"/api/groups/{group_id}")
    assert response.status_code == 404


def test_delete_group_with_students(client: TestClient, db_session: Session):
    """Test eliminar grupo con estudiantes debe fallar"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 30
    })
    group_id = group_response.json()["id"]
    
    # Crear subgroup y estudiante manualmente en la DB
    from app.models.academic import Group
    group = db_session.query(Group).filter(Group.id == group_id).first()
    
    # Crear subgroup
    subgroup = Subgroup(
        group_id=group_id,
        name="Subgrupo 1"
    )
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiante
    student = Student(
        identification="EST001",
        first_name="Juan",
        last_name="Pérez",
        date_of_birth=date(2010, 1, 1),
        subgroup_id=subgroup.id
    )
    db_session.add(student)
    db_session.commit()
    
    # Intentar eliminar grupo con estudiantes
    response = client.delete(f"/api/groups/{group_id}")
    
    assert response.status_code == 400
    assert "Cannot delete" in response.json()["detail"]


def test_get_group_students(client: TestClient, db_session: Session):
    """Test obtener estudiantes de un grupo"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A"
    })
    group_id = group_response.json()["id"]
    
    # Crear subgroup y estudiantes
    subgroup = Subgroup(
        group_id=group_id,
        name="Subgrupo 1"
    )
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    # Crear estudiantes
    student1 = Student(
        identification="EST001",
        first_name="María",
        last_name="García",
        date_of_birth=date(2010, 1, 1),
        subgroup_id=subgroup.id
    )
    student2 = Student(
        identification="EST002",
        first_name="Juan",
        last_name="Pérez",
        date_of_birth=date(2010, 2, 2),
        subgroup_id=subgroup.id
    )
    db_session.add_all([student1, student2])
    db_session.commit()
    
    # Obtener estudiantes
    response = client.get(f"/api/groups/{group_id}/students/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verificar orden alfabético por first_name
    assert data[0]["first_name"] == "Juan"
    assert data[1]["first_name"] == "María"


def test_group_student_count(client: TestClient, db_session: Session):
    """Test que student_count se calcula correctamente"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 30
    })
    group_id = group_response.json()["id"]
    
    # Inicialmente sin estudiantes
    response = client.get(f"/api/groups/{group_id}")
    assert response.json()["student_count"] == 0
    
    # Agregar estudiantes
    subgroup = Subgroup(group_id=group_id, name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    for i in range(3):
        student = Student(
            identification=f"EST00{i+1}",
            first_name=f"Estudiante{i+1}",
            last_name="Test",
            date_of_birth=date(2010, 1, 1),
            subgroup_id=subgroup.id
        )
        db_session.add(student)
    db_session.commit()
    
    # Verificar que student_count se actualizó
    response = client.get(f"/api/groups/{group_id}")
    assert response.json()["student_count"] == 3


def test_update_capacity_below_student_count(client: TestClient, db_session: Session):
    """Test actualizar capacidad por debajo del número de estudiantes debe fallar"""
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
    
    group_response = client.post("/api/groups/", json={
        "grade_id": grade["id"],
        "name": "Sección A",
        "capacity": 30
    })
    group_id = group_response.json()["id"]
    
    # Agregar 5 estudiantes
    subgroup = Subgroup(group_id=group_id, name="Subgrupo 1")
    db_session.add(subgroup)
    db_session.commit()
    db_session.refresh(subgroup)
    
    for i in range(5):
        student = Student(
            identification=f"EST00{i+1}",
            first_name=f"Estudiante{i+1}",
            last_name="Test",
            date_of_birth=date(2010, 1, 1),
            subgroup_id=subgroup.id
        )
        db_session.add(student)
    db_session.commit()
    
    # Intentar actualizar capacidad a 3 (menos que 5 estudiantes)
    response = client.put(f"/api/groups/{group_id}", json={
        "capacity": 3
    })
    
    assert response.status_code == 400
    assert "Cannot set capacity" in response.json()["detail"]
