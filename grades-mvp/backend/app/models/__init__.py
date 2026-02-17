# backend/app/models/__init__.py
"""
SQLAlchemy Models
"""

from app.database import Base

# TODO: Importar todos los modelos aquí para que init_db() los registre
# from app.models.user import User
# from app.models.academic import AcademicYear, Period, Grade, Group, Subgroup
# from app.models.student import Student
# etc...

__all__ = ["Base"]
