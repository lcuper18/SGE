"""
Schemas Pydantic para TeacherGroupAssignment — Story 4.2
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.schedule import Section


class TeacherGroupAssignmentBase(BaseModel):
    """Campos comunes"""
    teacher_id: int = Field(..., description="ID del usuario con rol teacher")
    group_id: int = Field(..., description="ID del grupo/sección escolar")
    subject: str = Field(..., min_length=2, max_length=200, description="Materia que imparte")
    section: Section = Field(default=Section.DAY, description="Jornada: day | night")
    period_id: Optional[int] = Field(
        default=None,
        description="ID del período académico (opcional; si es None aplica a todo el año)",
    )
    is_active: bool = Field(default=True)

    @field_validator("subject")
    @classmethod
    def subject_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("subject no puede estar vacío")
        return v.strip()


class TeacherGroupAssignmentCreate(TeacherGroupAssignmentBase):
    """Payload para crear una asignación"""
    pass


class TeacherGroupAssignmentUpdate(BaseModel):
    """Payload para actualizar una asignación (todos los campos opcionales)"""
    subject: Optional[str] = Field(default=None, min_length=2, max_length=200)
    section: Optional[Section] = None
    period_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("subject")
    @classmethod
    def subject_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("subject no puede estar vacío")
        return v.strip() if v else v


class TeacherGroupAssignmentResponse(TeacherGroupAssignmentBase):
    """Respuesta completa con campos calculados"""
    id: int
    teacher_username: str = Field(description="Username del profesor asignado")
    teacher_full_name: str = Field(description="Nombre completo del profesor")
    group_name: str = Field(description="Nombre del grupo/sección")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
