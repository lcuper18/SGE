"""
Service Layer para Academic Years, Periods y Grades
Contiene la lógica de negocio y operaciones CRUD
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.academic import AcademicYear, Period, Grade
from app.schemas.academic import (
    AcademicYearCreate, AcademicYearUpdate,
    PeriodCreate, PeriodUpdate,
    GradeCreate, GradeUpdate
)


# ============================================================================
# ACADEMIC YEAR SERVICE
# ============================================================================

class AcademicYearService:
    """Service para Academic Year operations"""
    
    @staticmethod
    def get_all(db: Session) -> List[AcademicYear]:
        """Obtener todos los años académicos"""
        return db.query(AcademicYear).order_by(AcademicYear.year.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, year_id: int) -> Optional[AcademicYear]:
        """Obtener año académico por ID"""
        return db.query(AcademicYear).filter(AcademicYear.id == year_id).first()
    
    @staticmethod
    def get_by_year(db: Session, year: int) -> Optional[AcademicYear]:
        """Obtener año académico por año (ej: 2026)"""
        return db.query(AcademicYear).filter(AcademicYear.year == year).first()
    
    @staticmethod
    def get_active(db: Session) -> Optional[AcademicYear]:
        """Obtener año académico activo"""
        return db.query(AcademicYear).filter(AcademicYear.is_active == True).first()
    
    @staticmethod
    def create(db: Session, data: AcademicYearCreate) -> AcademicYear:
        """Crear nuevo año académico"""
        # Validar que el año no exista
        existing = AcademicYearService.get_by_year(db, data.year)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Academic year {data.year} already exists"
            )
        
        # Si se marca como activo, desactivar otros años
        if data.is_active:
            AcademicYearService._deactivate_all(db)
        
        # Crear nuevo año
        academic_year = AcademicYear(**data.model_dump())
        db.add(academic_year)
        db.commit()
        db.refresh(academic_year)
        return academic_year
    
    @staticmethod
    def update(db: Session, year_id: int, data: AcademicYearUpdate) -> AcademicYear:
        """Actualizar año académico"""
        academic_year = AcademicYearService.get_by_id(db, year_id)
        if not academic_year:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Academic year {year_id} not found"
            )
        
        # Validar año único si se actualiza
        if data.year and data.year != academic_year.year:
            existing = AcademicYearService.get_by_year(db, data.year)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Academic year {data.year} already exists"
                )
        
        # Si se activa, desactivar otros
        if data.is_active and not academic_year.is_active:
            AcademicYearService._deactivate_all(db)
        
        # Actualizar campos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(academic_year, field, value)
        
        db.commit()
        db.refresh(academic_year)
        return academic_year
    
    @staticmethod
    def delete(db: Session, year_id: int) -> bool:
        """Eliminar año académico"""
        academic_year = AcademicYearService.get_by_id(db, year_id)
        if not academic_year:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Academic year {year_id} not found"
            )
        
        db.delete(academic_year)
        db.commit()
        return True
    
    @staticmethod
    def _deactivate_all(db: Session):
        """Desactivar todos los años académicos (helper privado)"""
        db.query(AcademicYear).update({AcademicYear.is_active: False})


# ============================================================================
# PERIOD SERVICE
# ============================================================================

class PeriodService:
    """Service para Period operations"""
    
    @staticmethod
    def get_all(db: Session, academic_year_id: Optional[int] = None) -> List[Period]:
        """Obtener todos los períodos, opcionalmente filtrados por año académico"""
        query = db.query(Period)
        if academic_year_id:
            query = query.filter(Period.academic_year_id == academic_year_id)
        return query.order_by(Period.start_date).all()
    
    @staticmethod
    def get_by_id(db: Session, period_id: int) -> Optional[Period]:
        """Obtener período por ID"""
        return db.query(Period).filter(Period.id == period_id).first()
    
    @staticmethod
    def create(db: Session, data: PeriodCreate) -> Period:
        """Crear nuevo período"""
        # Validar que el año académico exista
        academic_year = db.query(AcademicYear).filter(AcademicYear.id == data.academic_year_id).first()
        if not academic_year:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Academic year {data.academic_year_id} not found"
            )
        
        # Validar que no haya solapamiento de fechas
        PeriodService._validate_no_overlap(db, data.academic_year_id, data.start_date, data.end_date)
        
        # Si se marca como activo, desactivar otros períodos del mismo año
        if data.is_active:
            PeriodService._deactivate_all_in_year(db, data.academic_year_id)
        
        # Crear período
        period = Period(**data.model_dump())
        db.add(period)
        db.commit()
        db.refresh(period)
        return period
    
    @staticmethod
    def update(db: Session, period_id: int, data: PeriodUpdate) -> Period:
        """Actualizar período"""
        period = PeriodService.get_by_id(db, period_id)
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Period {period_id} not found"
            )
        
        # Preparar datos actualizados
        update_data = data.model_dump(exclude_unset=True)
        
        # Validar solapamiento si se actualizan fechas
        start_date = update_data.get('start_date', period.start_date)
        end_date = update_data.get('end_date', period.end_date)
        academic_year_id = update_data.get('academic_year_id', period.academic_year_id)
        
        PeriodService._validate_no_overlap(db, academic_year_id, start_date, end_date, exclude_id=period_id)
        
        # Si se activa, desactivar otros
        if update_data.get('is_active') and not period.is_active:
            PeriodService._deactivate_all_in_year(db, academic_year_id)
        
        # Actualizar
        for field, value in update_data.items():
            setattr(period, field, value)
        
        db.commit()
        db.refresh(period)
        return period
    
    @staticmethod
    def delete(db: Session, period_id: int) -> bool:
        """Eliminar período"""
        period = PeriodService.get_by_id(db, period_id)
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Period {period_id} not found"
            )
        
        db.delete(period)
        db.commit()
        return True
    
    @staticmethod
    def _validate_no_overlap(db: Session, academic_year_id: int, start_date, end_date, exclude_id: Optional[int] = None):
        """Validar que no haya solapamiento de fechas"""
        query = db.query(Period).filter(
            Period.academic_year_id == academic_year_id,
            Period.start_date <= end_date,
            Period.end_date >= start_date
        )
        
        if exclude_id:
            query = query.filter(Period.id != exclude_id)
        
        overlap = query.first()
        if overlap:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Period dates overlap with existing period: {overlap.name}"
            )
    
    @staticmethod
    def _deactivate_all_in_year(db: Session, academic_year_id: int):
        """Desactivar todos los períodos de un año académico"""
        db.query(Period).filter(Period.academic_year_id == academic_year_id).update({Period.is_active: False})


# ============================================================================
# GRADE SERVICE
# ============================================================================

class GradeService:
    """Service para Grade operations"""
    
    @staticmethod
    def get_all(db: Session, academic_year_id: Optional[int] = None) -> List[Grade]:
        """Obtener todos los grados, opcionalmente filtrados por año académico"""
        query = db.query(Grade)
        if academic_year_id:
            query = query.filter(Grade.academic_year_id == academic_year_id)
        return query.order_by(Grade.level).all()
    
    @staticmethod
    def get_by_id(db: Session, grade_id: int) -> Optional[Grade]:
        """Obtener grado por ID"""
        return db.query(Grade).filter(Grade.id == grade_id).first()
    
    @staticmethod
    def create(db: Session, data: GradeCreate) -> Grade:
        """Crear nuevo grado"""
        # Validar que el año académico exista
        academic_year = db.query(AcademicYear).filter(AcademicYear.id == data.academic_year_id).first()
        if not academic_year:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Academic year {data.academic_year_id} not found"
            )
        
        # Validar que el level sea único para este año académico
        existing = db.query(Grade).filter(
            and_(
                Grade.academic_year_id == data.academic_year_id,
                Grade.level == data.level
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Grade level {data.level} already exists for this academic year"
            )
        
        # Crear grado
        grade = Grade(**data.model_dump())
        db.add(grade)
        db.commit()
        db.refresh(grade)
        return grade
    
    @staticmethod
    def update(db: Session, grade_id: int, data: GradeUpdate) -> Grade:
        """Actualizar grado"""
        grade = GradeService.get_by_id(db, grade_id)
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {grade_id} not found"
            )
        
        # Validar level único si se actualiza
        update_data = data.model_dump(exclude_unset=True)
        if 'level' in update_data or 'academic_year_id' in update_data:
            new_level = update_data.get('level', grade.level)
            new_year_id = update_data.get('academic_year_id', grade.academic_year_id)
            
            existing = db.query(Grade).filter(
                and_(
                    Grade.academic_year_id == new_year_id,
                    Grade.level == new_level,
                    Grade.id != grade_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Grade level {new_level} already exists for this academic year"
                )
        
        # Actualizar
        for field, value in update_data.items():
            setattr(grade, field, value)
        
        db.commit()
        db.refresh(grade)
        return grade
    
    @staticmethod
    def delete(db: Session, grade_id: int) -> bool:
        """Eliminar grado (solo si no tiene grupos)"""
        grade = GradeService.get_by_id(db, grade_id)
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {grade_id} not found"
            )
        
        # Verificar si tiene grupos asociados
        if grade.groups:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete grade with existing groups. Use soft delete instead."
            )
        
        db.delete(grade)
        db.commit()
        return True
