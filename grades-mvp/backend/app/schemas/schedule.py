"""
Schemas Pydantic para TimeSlot — Story 4.1
"""
from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.schedule import SlotType, LessonType, Section, Weekday


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class TimeSlotBase(BaseModel):
    """Campos comunes a create/update/response"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del bloque (ej: 'Bloque 1')")
    start_time: time = Field(..., description="Hora de inicio (HH:MM)")
    end_time: time = Field(..., description="Hora de fin (HH:MM)")
    slot_type: SlotType = Field(..., description="Tipo: lesson | break | lunch")
    lesson_type: Optional[LessonType] = Field(
        None, description="Tipo de lección: academic | technical (solo si slot_type=lesson)"
    )
    weekday: Weekday = Field(..., description="Día de semana: 0=Lunes … 6=Domingo")
    section: Section = Field(..., description="Jornada: day | night")
    is_active: bool = Field(default=True)

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v, info):
        """end_time debe ser posterior a start_time"""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time debe ser posterior a start_time")
        return v

    @model_validator(mode="after")
    def validate_lesson_type_consistency(self) -> "TimeSlotBase":
        """
        Si slot_type = lesson → lesson_type es requerido.
        Si slot_type != lesson → lesson_type debe ser None.
        """
        if self.slot_type == SlotType.LESSON and self.lesson_type is None:
            raise ValueError("lesson_type es requerido cuando slot_type es 'lesson'")
        if self.slot_type != SlotType.LESSON and self.lesson_type is not None:
            raise ValueError("lesson_type solo aplica cuando slot_type es 'lesson'")
        return self


class TimeSlotCreate(TimeSlotBase):
    """Schema para crear un TimeSlot"""
    pass


class TimeSlotUpdate(BaseModel):
    """Schema para actualizar un TimeSlot (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_type: Optional[SlotType] = None
    lesson_type: Optional[LessonType] = None
    weekday: Optional[Weekday] = None
    section: Optional[Section] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_times(self) -> "TimeSlotUpdate":
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("end_time debe ser posterior a start_time")
        return self


class TimeSlotResponse(TimeSlotBase):
    """Schema de respuesta — incluye campos calculados"""
    id: int
    duration_minutes: int = Field(..., description="Duración real en minutos")
    academic_equivalent_minutes: float = Field(
        ..., description="Minutos equivalentes académicos (técnico × 1.5)"
    )

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Schema para el seed de plantillas
# ---------------------------------------------------------------------------

class TemplateName(str):
    DAY = "day"
    NIGHT = "night"


class SeedTemplateRequest(BaseModel):
    """Solicitud para generar plantilla de horario por defecto"""
    section: Section = Field(..., description="Jornada a generar: day | night")
    weekdays: list[Weekday] = Field(
        default=[Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY,
                 Weekday.THURSDAY, Weekday.FRIDAY],
        description="Días de la semana a generar (default: lunes a viernes)",
    )
    overwrite: bool = Field(
        default=False,
        description="Si True, elimina los slots existentes de los días indicados antes de crear",
    )


class SeedTemplateResponse(BaseModel):
    """Resultado del seed de plantilla"""
    created: int
    skipped: int
    overwritten: int
    message: str
