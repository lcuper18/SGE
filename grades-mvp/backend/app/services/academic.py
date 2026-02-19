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


# ============================================================================
# GROUP SERVICE
# ============================================================================

class GroupService:
    """Service para Group operations"""
    
    @staticmethod
    def get_all(db: Session, grade_id: Optional[int] = None, academic_year_id: Optional[int] = None) -> List:
        """Obtener todos los grupos, opcionalmente filtrados"""
        from app.models.academic import Group, Grade
        
        query = db.query(Group)
        
        if grade_id:
            query = query.filter(Group.grade_id == grade_id)
        
        if academic_year_id:
            query = query.join(Grade).filter(Grade.academic_year_id == academic_year_id)
        
        return query.order_by(Group.name).all()
    
    @staticmethod
    def get_by_id(db: Session, group_id: int):
        """Obtener grupo por ID"""
        from app.models.academic import Group
        return db.query(Group).filter(Group.id == group_id).first()
    
    @staticmethod
    def get_student_count(db: Session, group_id: int) -> int:
        """Obtener número de estudiantes en un grupo"""
        from app.models.student import Student
        from app.models.academic import Subgroup
        
        # Contar estudiantes a través de subgroups
        count = db.query(Student).join(
            Subgroup, Student.subgroup_id == Subgroup.id
        ).filter(
            Subgroup.group_id == group_id
        ).count()
        
        return count
    
    @staticmethod
    def create(db: Session, data) -> "Group":
        """Crear nuevo grupo"""
        from app.models.academic import Group, Grade
        
        # Validar que el grado exista
        grade = db.query(Grade).filter(Grade.id == data.grade_id).first()
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grade {data.grade_id} not found"
            )
        
        # Validar nombre único por grado
        existing = db.query(Group).filter(
            and_(
                Group.grade_id == data.grade_id,
                Group.name == data.name
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group '{data.name}' already exists for this grade"
            )
        
        # Crear grupo
        group = Group(**data.model_dump())
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def update(db: Session, group_id: int, data) -> "Group":
        """Actualizar grupo"""
        from app.models.academic import Group
        
        group = GroupService.get_by_id(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Validar nombre único si se actualiza
        update_data = data.model_dump(exclude_unset=True)
        
        if 'name' in update_data or 'grade_id' in update_data:
            new_name = update_data.get('name', group.name)
            new_grade_id = update_data.get('grade_id', group.grade_id)
            
            existing = db.query(Group).filter(
                and_(
                    Group.grade_id == new_grade_id,
                    Group.name == new_name,
                    Group.id != group_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Group '{new_name}' already exists for this grade"
                )
        
        # Validar capacidad si hay estudiantes
        if 'capacity' in update_data and update_data['capacity']:
            student_count = GroupService.get_student_count(db, group_id)
            if student_count > update_data['capacity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot set capacity to {update_data['capacity']}. Group has {student_count} students."
                )
        
        # Actualizar
        for field, value in update_data.items():
            setattr(group, field, value)
        
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def delete(db: Session, group_id: int) -> bool:
        """Eliminar grupo (solo si no tiene estudiantes)"""
        from app.models.academic import Group
        
        group = GroupService.get_by_id(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Verificar si tiene estudiantes
        student_count = GroupService.get_student_count(db, group_id)
        if student_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete group with {student_count} students"
            )
        
        db.delete(group)
        db.commit()
        return True
    
    @staticmethod
    def get_students(db: Session, group_id: int) -> List:
        """Obtener estudiantes de un grupo"""
        from app.models.student import Student
        from app.models.academic import Subgroup
        
        # Validar que el grupo exista
        group = GroupService.get_by_id(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Obtener estudiantes a través de subgroups
        students = db.query(Student).join(
            Subgroup, Student.subgroup_id == Subgroup.id
        ).filter(
            Subgroup.group_id == group_id
        ).order_by(Student.first_name, Student.last_name).all()
        
        return students


# ============================================================================
# StudentService - CRUD para Students
# ============================================================================

class StudentService:
    """
    Servicio para gestionar estudiantes
    Incluye búsqueda, paginación y soft delete
    """
    
    @staticmethod
    def get_all(
        db: Session,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        subgroup_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50
    ):
        """
        Obtener todos los estudiantes con filtros y paginación
        
        Args:
            search_query: Buscar por nombre o identification
            is_active: Filtrar por estado activo/inactivo
            subgroup_id: Filtrar por subgrupo
            page: Número de página (1-based)
            page_size: Tamaño de página
        """
        from app.models.student import Student
        
        query = db.query(Student)
        
        # Filtro de búsqueda
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                (Student.identification.ilike(search_pattern)) |
                (Student.first_name.ilike(search_pattern)) |
                (Student.last_name.ilike(search_pattern))
            )
        
        # Filtro por estado
        if is_active is not None:
            query = query.filter(Student.is_active == is_active)
        
        # Filtro por subgrupo
        if subgroup_id:
            query = query.filter(Student.subgroup_id == subgroup_id)
        
        # Ordenar por nombre
        query = query.order_by(Student.first_name, Student.last_name)
        
        # Paginación
        offset = (page - 1) * page_size
        students = query.offset(offset).limit(page_size).all()
        
        # Contar total
        total = query.count()
        
        return {
            "students": students,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def get_by_id(db: Session, student_id: int):
        """Obtener estudiante por ID"""
        from app.models.student import Student
        return db.query(Student).filter(Student.id == student_id).first()
    
    @staticmethod
    def get_by_identification(db: Session, identification: str):
        """Obtener estudiante por número de identificación"""
        from app.models.student import Student
        return db.query(Student).filter(Student.identification == identification).first()
    
    @staticmethod
    def create(db: Session, data: dict):
        """
        Crear nuevo estudiante
        Valida que identification sea único
        """
        from app.models.student import Student
        from app.models.academic import Subgroup
        
        # Validar identification único
        existing = StudentService.get_by_identification(db, data["identification"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with identification {data['identification']} already exists"
            )
        
        # Validar que el subgrupo exista
        subgroup = db.query(Subgroup).filter(Subgroup.id == data["subgroup_id"]).first()
        if not subgroup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subgroup {data['subgroup_id']} not found"
            )
        
        student = Student(**data)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def update(db: Session, student_id: int, data: dict):
        """
        Actualizar estudiante
        Valida identification único si se está cambiando
        """
        from app.models.student import Student
        from app.models.academic import Subgroup
        
        student = StudentService.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Validar identification único si se está cambiando
        if "identification" in data and data["identification"] != student.identification:
            existing = StudentService.get_by_identification(db, data["identification"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student with identification {data['identification']} already exists"
                )
        
        # Validar subgrupo si se está cambiando
        if "subgroup_id" in data and data["subgroup_id"] != student.subgroup_id:
            subgroup = db.query(Subgroup).filter(Subgroup.id == data["subgroup_id"]).first()
            if not subgroup:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subgroup {data['subgroup_id']} not found"
                )
        
        # Actualizar campos
        for key, value in data.items():
            setattr(student, key, value)
        
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def delete(db: Session, student_id: int):
        """
        Soft delete: Marcar estudiante como inactivo
        """
        from app.models.student import Student
        
        student = StudentService.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Soft delete
        student.is_active = False
        db.commit()
        db.refresh(student)
        return student
