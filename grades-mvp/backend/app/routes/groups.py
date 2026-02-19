"""
Groups Routes
Endpoints CRUD para gestión de grupos/secciones
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.academic import GroupCreate, GroupUpdate, GroupResponse
from app.services.academic import GroupService

router = APIRouter(prefix="/api/groups", tags=["Groups"])


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo grupo/sección
    
    - **grade_id**: ID del grado al que pertenece
    - **name**: Nombre del grupo (ej: "Sección A", "Grupo 1")
    - **capacity** (opcional): Capacidad máxima de estudiantes
    
    Validaciones:
    - El nombre debe ser único por grado
    - El grado debe existir
    """
    group = GroupService.create(db, data)
    
    # Agregar student_count al response
    response = GroupResponse.model_validate(group)
    response.student_count = GroupService.get_student_count(db, group.id)
    return response


@router.get("/", response_model=List[GroupResponse])
def get_groups(
    grade_id: Optional[int] = Query(None, description="Filtrar por grado"),
    academic_year_id: Optional[int] = Query(None, description="Filtrar por año académico"),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los grupos
    
    - **grade_id** (opcional): Filtrar por grado específico
    - **academic_year_id** (opcional): Filtrar por año académico
    
    Retorna lista ordenada por nombre
    """
    groups = GroupService.get_all(db, grade_id, academic_year_id)
    
    # Agregar student_count a cada grupo
    result = []
    for group in groups:
        response = GroupResponse.model_validate(group)
        response.student_count = GroupService.get_student_count(db, group.id)
        result.append(response)
    
    return result


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un grupo por ID
    
    - **group_id**: ID del grupo
    """
    group = GroupService.get_by_id(db, group_id)
    if not group:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    # Agregar student_count al response
    response = GroupResponse.model_validate(group)
    response.student_count = GroupService.get_student_count(db, group_id)
    return response


@router.get("/{group_id}/students/")
def get_group_students(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener estudiantes de un grupo
    
    - **group_id**: ID del grupo
    
    Retorna lista de estudiantes ordenados por nombre
    """
    students = GroupService.get_students(db, group_id)
    
    # Convertir a dict básico por ahora (después usaremos StudentResponse)
    return [
        {
            "id": s.id,
            "identification": s.identification,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "subgroup_id": s.subgroup_id
        }
        for s in students
    ]


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    data: GroupUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un grupo
    
    - **group_id**: ID del grupo
    - Todos los campos son opcionales
    - Valida que el nombre sea único si se actualiza
    - Valida que la capacidad no sea menor al número actual de estudiantes
    """
    group = GroupService.update(db, group_id, data)
    
    # Agregar student_count al response
    response = GroupResponse.model_validate(group)
    response.student_count = GroupService.get_student_count(db, group_id)
    return response


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un grupo
    
    - **group_id**: ID del grupo
    - Solo se puede eliminar si no tiene estudiantes
    """
    GroupService.delete(db, group_id)
    return None
