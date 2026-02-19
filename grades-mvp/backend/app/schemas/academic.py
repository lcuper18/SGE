"""
Schemas de validación para modelos académicos
Define request/response models para Academic Years, Periods y Grades
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ACADEMIC YEAR SCHEMAS
# ============================================================================

class AcademicYearBase(BaseModel):
    """Schema base para Academic Year"""
    year: int = Field(..., ge=2020, le=2100, description="Año académico (ej: 2026)")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo")
    is_active: bool = Field(default=False, description="Si es el año activo")


class AcademicYearCreate(AcademicYearBase):
    """Schema para crear Academic Year"""
    pass


class AcademicYearUpdate(BaseModel):
    """Schema para actualizar Academic Year (todos los campos opcionales)"""
    year: Optional[int] = Field(None, ge=2020, le=2100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class AcademicYearResponse(AcademicYearBase):
    """Schema de respuesta para Academic Year"""
    id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# PERIOD SCHEMAS
# ============================================================================

class PeriodBase(BaseModel):
    """Schema base para Period"""
    academic_year_id: int = Field(..., gt=0, description="ID del año académico")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del período")
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: date = Field(..., description="Fecha de fin")
    is_active: bool = Field(default=False, description="Si es el período activo")
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validar que end_date sea posterior a start_date"""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date debe ser posterior a start_date')
        return v


class PeriodCreate(PeriodBase):
    """Schema para crear Period"""
    pass


class PeriodUpdate(BaseModel):
    """Schema para actualizar Period"""
    academic_year_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class PeriodResponse(PeriodBase):
    """Schema de respuesta para Period"""
    id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# GRADE SCHEMAS
# ============================================================================

class GradeBase(BaseModel):
    """Schema base para Grade"""
    academic_year_id: int = Field(..., gt=0, description="ID del año académico")
    level: int = Field(..., ge=1, le=6, description="Nivel educativo (1-6)")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del grado")
    description: Optional[str] = Field(None, max_length=500, description="Descripción opcional")


class GradeCreate(GradeBase):
    """Schema para crear Grade"""
    pass


class GradeUpdate(BaseModel):
    """Schema para actualizar Grade"""
    academic_year_id: Optional[int] = Field(None, gt=0)
    level: Optional[int] = Field(None, ge=1, le=6)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GradeResponse(GradeBase):
    """Schema de respuesta para Grade"""
    id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# GROUP SCHEMAS
# ============================================================================

class GroupBase(BaseModel):
    """Schema base para Group"""
    grade_id: int = Field(..., gt=0, description="ID del grado")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del grupo")
    capacity: Optional[int] = Field(None, gt=0, le=100, description="Capacidad máxima de estudiantes")


class GroupCreate(GroupBase):
    """Schema para crear Group"""
    pass


class GroupUpdate(BaseModel):
    """Schema para actualizar Group"""
    grade_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    capacity: Optional[int] = Field(None, gt=0, le=100)


class GroupResponse(GroupBase):
    """Schema de respuesta para Group"""
    id: int
    student_count: int = Field(default=0, description="Número de estudiantes en el grupo")
    
    class Config:
        from_attributes = True


# ============================================================================
# Student Schemas
# ============================================================================

class StudentBase(BaseModel):
    """Schema base para Student"""
    identification: str = Field(..., min_length=1, max_length=50, description="Número de identificación único")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellidos")
    date_of_birth: date = Field(..., description="Fecha de nacimiento")
    subgroup_id: int = Field(..., gt=0, description="ID del subgrupo")


class StudentCreate(StudentBase):
    """Schema para crear Student"""
    pass


class StudentUpdate(BaseModel):
    """Schema para actualizar Student"""
    identification: Optional[str] = Field(None, min_length=1, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    subgroup_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Schema de respuesta para Student"""
    id: int
    is_active: bool
    full_name: str = Field(description="Nombre completo")
    
    class Config:
        from_attributes = True
