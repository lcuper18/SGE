"""
Rutas para Students API
Endpoints CRUD con búsqueda y paginación
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.academic import StudentCreate, StudentUpdate, StudentResponse
from app.services.academic import StudentService
from app.dependencies import require_authenticated, require_admin_or_coordinator

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Crear nuevo estudiante
    
    Validaciones:
    - identification debe ser único
    - subgroup_id debe existir
    """
    student_data = data.model_dump()
    student = StudentService.create(db, student_data)
    return student


@router.get("/", response_model=dict)
def get_students(
    search: Optional[str] = Query(None, description="Buscar por nombre o identification"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    subgroup_id: Optional[int] = Query(None, description="Filtrar por subgrupo"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """
    Obtener lista de estudiantes con filtros y paginación
    
    Búsqueda por:
    - identification
    - first_name
    - last_name
    
    Paginación por defecto: 50 estudiantes por página
    """
    result = StudentService.get_all(
        db=db,
        search_query=search,
        is_active=is_active,
        subgroup_id=subgroup_id,
        page=page,
        page_size=page_size
    )
    
    # Convertir estudiantes a response schema
    students = [StudentResponse.model_validate(s) for s in result["students"]]
    
    return {
        "students": students,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"]
    }


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """Obtener estudiante por ID"""
    student = StudentService.get_by_id(db, student_id)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Actualizar estudiante
    
    Validaciones:
    - Si se cambia identification, debe ser único
    - Si se cambia subgroup_id, debe existir
    """
    update_data = data.model_dump(exclude_unset=True)
    student = StudentService.update(db, student_id, update_data)
    return student


@router.delete("/{student_id}", response_model=StudentResponse)
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Soft delete: Marcar estudiante como inactivo
    
    No elimina el registro, solo cambia is_active a False
    """
    student = StudentService.delete(db, student_id)
    return student
