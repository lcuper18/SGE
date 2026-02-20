"""
Teacher Group Assignments Routes — Story 4.2
Endpoints CRUD para asignaciones de profesor a grupo/materia
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.schedule import Section
from app.schemas.teacher_assignments import (
    TeacherGroupAssignmentCreate,
    TeacherGroupAssignmentUpdate,
    TeacherGroupAssignmentResponse,
)
from app.services.teacher_assignments import TeacherAssignmentService
from app.dependencies import require_authenticated, require_admin_or_coordinator

router = APIRouter(prefix="/api/teacher-assignments", tags=["Teacher Assignments"])


@router.post("/", response_model=TeacherGroupAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    data: TeacherGroupAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """
    Asignar un profesor a un grupo para una materia específica.

    - **teacher_id**: ID del usuario con rol teacher/coordinator
    - **group_id**: ID del grupo/sección escolar
    - **subject**: Materia que imparte (ej: "Matemáticas")
    - **section**: Jornada — day | night
    - **period_id**: ID del período académico (opcional)
    """
    assignment = TeacherAssignmentService.create(db, data)
    return TeacherAssignmentService.to_response_dict(assignment)


@router.get("/", response_model=List[TeacherGroupAssignmentResponse])
def get_assignments(
    teacher_id: Optional[int] = Query(default=None, description="Filtrar por teacher_id"),
    group_id: Optional[int] = Query(default=None, description="Filtrar por group_id"),
    section: Optional[Section] = Query(default=None, description="Filtrar por sección"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Listar asignaciones con filtros opcionales.

    Los profesores autenticados pueden usar este endpoint;
    para ver solo las propias usar **GET /my/**.
    """
    section_val = section.value if section else None
    assignments = TeacherAssignmentService.get_all(db, teacher_id, group_id, section_val, is_active)
    return [TeacherAssignmentService.to_response_dict(a) for a in assignments]


@router.get("/my/", response_model=List[TeacherGroupAssignmentResponse])
def get_my_assignments(
    section: Optional[Section] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Devuelve las asignaciones del usuario autenticado como profesor.

    Útil para que el teacher vea sus grupos sin necesitar saber su propio teacher_id.
    """
    section_val = section.value if section else None
    assignments = TeacherAssignmentService.get_all(
        db,
        teacher_id=current_user.id,
        section=section_val,
        is_active=is_active,
    )
    return [TeacherAssignmentService.to_response_dict(a) for a in assignments]


@router.get("/{assignment_id}", response_model=TeacherGroupAssignmentResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """Obtener una asignación por ID."""
    assignment = TeacherAssignmentService.get_by_id(db, assignment_id)
    return TeacherAssignmentService.to_response_dict(assignment)


@router.put("/{assignment_id}", response_model=TeacherGroupAssignmentResponse)
def update_assignment(
    assignment_id: int,
    data: TeacherGroupAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """
    Actualizar una asignación (materia, sección, período o estado activo).

    Para cambiar teacher_id o group_id, eliminar y crear una nueva asignación.
    """
    assignment = TeacherAssignmentService.update(db, assignment_id, data)
    return TeacherAssignmentService.to_response_dict(assignment)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """Eliminar una asignación (hard delete)."""
    TeacherAssignmentService.delete(db, assignment_id)
