"""
Grades Routes
Endpoints CRUD para gestión de grados/niveles educativos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.academic import GradeCreate, GradeUpdate, GradeResponse
from app.services.academic import GradeService
from app.dependencies import require_authenticated, require_admin_or_coordinator

router = APIRouter(prefix="/api/grades", tags=["Grades"])


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Crear un nuevo grado/nivel educativo
    
    - **academic_year_id**: ID del año académico
    - **level**: Nivel educativo (1-6)
    - **name**: Nombre del grado (ej: "Primer Grado")
    - **description** (opcional): Descripción adicional
    
    Validaciones:
    - El nivel debe ser único por año académico
    - El nivel debe estar entre 1 y 6
    """
    return GradeService.create(db, data)


@router.get("/", response_model=List[GradeResponse])
def get_grades(
    academic_year_id: Optional[int] = Query(None, description="Filtrar por año académico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """
    Obtener todos los grados/niveles
    
    - **academic_year_id** (opcional): Filtrar por año académico específico
    
    Retorna lista ordenada por nivel (1-6)
    """
    return GradeService.get_all(db, academic_year_id)


@router.get("/{grade_id}", response_model=GradeResponse)
def get_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """
    Obtener un grado por ID
    
    - **grade_id**: ID del grado
    """
    grade = GradeService.get_by_id(db, grade_id)
    if not grade:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade {grade_id} not found"
        )
    return grade


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: int,
    data: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Actualizar un grado
    
    - **grade_id**: ID del grado
    - Todos los campos son opcionales
    - Valida que el nivel sea único si se actualiza
    """
    return GradeService.update(db, grade_id, data)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Eliminar un grado
    
    - **grade_id**: ID del grado
    - Solo se puede eliminar si no tiene grupos asociados
    """
    GradeService.delete(db, grade_id)
    return None
