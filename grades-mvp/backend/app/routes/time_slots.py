"""
Time Slots Routes — Story 4.1
Endpoints CRUD para bloques horarios + seed de plantilla
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.schedule import SlotType, Section, Weekday
from app.schemas.schedule import (
    TimeSlotCreate,
    TimeSlotUpdate,
    TimeSlotResponse,
    SeedTemplateRequest,
    SeedTemplateResponse,
)
from app.services.schedule import TimeSlotService
from app.dependencies import require_authenticated, require_admin_or_coordinator

router = APIRouter(prefix="/api/time-slots", tags=["Time Slots"])


@router.post("/", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
def create_time_slot(
    data: TimeSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """
    Crear un nuevo bloque horario.

    - **name**: Nombre del bloque (ej: "Bloque 1", "Recreo")
    - **start_time / end_time**: Horario en formato HH:MM
    - **slot_type**: lesson | break | lunch
    - **lesson_type**: academic | technical (obligatorio si slot_type = lesson)
    - **weekday**: 0 = Lunes … 6 = Domingo
    - **section**: day | night

    Validaciones:
    - end_time debe ser posterior a start_time
    - No puede solaparse con bloques existentes del mismo día y sección
    - lesson_type solo aplica cuando slot_type = lesson
    """
    return TimeSlotService.create(db, data)


@router.get("/", response_model=List[TimeSlotResponse])
def get_time_slots(
    weekday: Optional[int] = Query(None, ge=0, le=6, description="Filtrar por día (0=Lunes, 6=Domingo)"),
    section: Optional[Section] = Query(None, description="Filtrar por jornada: day | night"),
    slot_type: Optional[SlotType] = Query(None, description="Filtrar por tipo: lesson | break | lunch"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Obtener todos los bloques horarios.

    Retorna lista ordenada por día → hora de inicio.
    """
    return TimeSlotService.get_all(
        db,
        weekday=weekday,
        section=section.value if section else None,
        slot_type=slot_type.value if slot_type else None,
        is_active=is_active,
    )


@router.get("/{slot_id}", response_model=TimeSlotResponse)
def get_time_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """Obtener un bloque horario por ID."""
    slot = TimeSlotService.get_by_id(db, slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimeSlot {slot_id} not found",
        )
    return slot


@router.put("/{slot_id}", response_model=TimeSlotResponse)
def update_time_slot(
    slot_id: int,
    data: TimeSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """
    Actualizar un bloque horario.

    Todos los campos son opcionales.
    Re-valida solapamiento si se cambia el horario, día o sección.
    """
    return TimeSlotService.update(db, slot_id, data)


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """Eliminar un bloque horario."""
    TimeSlotService.delete(db, slot_id)
    return None


@router.post("/seed-template", response_model=SeedTemplateResponse, status_code=status.HTTP_201_CREATED)
def seed_default_template(
    data: SeedTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator),
):
    """
    Genera los bloques horarios por defecto para una jornada.

    **Plantilla diurna (day):** 13 bloques de Lun–Vie
    - 6 bloques académicos (40 min) + 4 bloques técnicos (60 min)
    - 2 recreos (20 min) + 1 almuerzo (60 min)

    **Plantilla nocturna (night):** 5 bloques de Lun–Vie
    - 3 bloques técnicos (60 min) + 1 académico (40 min)
    - 1 recreo (20 min)

    Si **overwrite = true**, elimina los bloques existentes de los días indicados antes de crear.
    Si un bloque (mismo nombre + día + sección) ya existe, se omite.
    """
    weekdays = [w.value for w in data.weekdays]
    result = TimeSlotService.seed_template(
        db,
        section=data.section.value,
        weekdays=weekdays,
        overwrite=data.overwrite,
    )
    total = result["created"] + result["skipped"] + result["overwritten"]
    return SeedTemplateResponse(
        created=result["created"],
        skipped=result["skipped"],
        overwritten=result["overwritten"],
        message=(
            f"{result['created']} creados, "
            f"{result['overwritten']} sobreescritos, "
            f"{result['skipped']} omitidos "
            f"de {total} bloques en {len(weekdays)} días."
        ),
    )
