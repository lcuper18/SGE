# backend/app/models/__init__.py
"""
SQLAlchemy Models
Importa todos los modelos para registro en Base.metadata
"""

from app.database import Base

# Modelos académicos
from app.models.academic import (
    AcademicYear,
    Period,
    Grade,
    Group,
    Subgroup
)

# Modelo de usuario con autenticación Argon2id
from app.models.user import User

# Modelo de estudiante
from app.models.student import Student

# Modelos de horario
from app.models.schedule import TimeSlot


# Exportar todos los modelos
__all__ = [
    "Base",
    "AcademicYear",
    "Period",
    "Grade",
    "Group",
    "Subgroup",
    "User",
    "Student",
    "TimeSlot",
]
