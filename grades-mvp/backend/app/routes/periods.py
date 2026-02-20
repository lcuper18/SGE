"""
Periods Routes
Endpoints CRUD para gestión de períodos académicos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.academic import PeriodCreate, PeriodUpdate, PeriodResponse
from app.services.academic import PeriodService
from app.dependencies import require_authenticated, require_admin_or_coordinator

router = APIRouter(prefix="/api/periods", tags=["Periods"])


@router.post("/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
def create_period(
    data: PeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Crear un nuevo período académico
    
    - **academic_year_id**: ID del año académico al que pertenece
    - **name**: Nombre del período (ej: "Primer Trimestre")
    - **start_date**: Fecha de inicio
    - **end_date**: Fecha de fin (debe ser posterior a start_date)
    - **is_active**: Si es el período activo
    
    Validaciones:
    - Las fechas no deben solaparse con otros períodos del mismo año
    - end_date debe ser posterior a start_date
    """
    return PeriodService.create(db, data)


@router.get("/", response_model=List[PeriodResponse])
def get_periods(
    academic_year_id: Optional[int] = Query(None, description="Filtrar por año académico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """
    Obtener todos los períodos académicos
    
    - **academic_year_id** (opcional): Filtrar por año académico específico
    
    Retorna lista ordenada por fecha de inicio
    """
    return PeriodService.get_all(db, academic_year_id)


@router.get("/{period_id}", response_model=PeriodResponse)
def get_period(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated)
):
    """
    Obtener un período académico por ID
    
    - **period_id**: ID del período
    """
    period = PeriodService.get_by_id(db, period_id)
    if not period:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Period {period_id} not found"
        )
    return period


@router.put("/{period_id}", response_model=PeriodResponse)
def update_period(
    period_id: int,
    data: PeriodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Actualizar un período académico
    
    - **period_id**: ID del período
    - Todos los campos son opcionales
    - Si se activa un período, los demás del mismo año se desactivan automáticamente
    - Valida que las fechas no solapen con otros períodos
    """
    return PeriodService.update(db, period_id, data)


@router.delete("/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_period(
    period_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """
    Eliminar un período académico
    
    - **period_id**: ID del período
    """
    PeriodService.delete(db, period_id)
    return None
