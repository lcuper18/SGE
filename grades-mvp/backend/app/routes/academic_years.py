"""
Academic Years Routes
Endpoints CRUD para gestión de años académicos
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.academic import AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse
from app.services.academic import AcademicYearService

router = APIRouter(prefix="/api/academic-years", tags=["Academic Years"])


@router.post("/", response_model=AcademicYearResponse, status_code=status.HTTP_201_CREATED)
def create_academic_year(
    data: AcademicYearCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo año académico
    
    - **year**: Año académico (ej: 2026)
    - **name**: Nombre descriptivo
    - **is_active**: Si es el año activo (solo uno puede estar activo)
    """
    return AcademicYearService.create(db, data)


@router.get("/", response_model=List[AcademicYearResponse])
def get_academic_years(db: Session = Depends(get_db)):
    """
    Obtener todos los años académicos
    
    Retorna lista ordenada por año (más recientes primero)
    """
    return AcademicYearService.get_all(db)


@router.get("/{year_id}", response_model=AcademicYearResponse)
def get_academic_year(
    year_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un año académico por ID
    
    - **year_id**: ID del año académico
    """
    academic_year = AcademicYearService.get_by_id(db, year_id)
    if not academic_year:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic year {year_id} not found"
        )
    return academic_year


@router.put("/{year_id}", response_model=AcademicYearResponse)
def update_academic_year(
    year_id: int,
    data: AcademicYearUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un año académico
    
    - **year_id**: ID del año académico
    - Todos los campos son opcionales
    - Si se activa un año, los demás se desactivan automáticamente
    """
    return AcademicYearService.update(db, year_id, data)


@router.delete("/{year_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic_year(
    year_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un año académico
    
    - **year_id**: ID del año académico
    - Eliminará en cascada todos los períodos y grados asociados
    """
    AcademicYearService.delete(db, year_id)
    return None
