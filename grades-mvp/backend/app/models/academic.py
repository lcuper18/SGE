"""
Modelos académicos para SGE Grades MVP
Define la estructura de años, períodos, grados, grupos y subgrupos
"""
from datetime import datetime, date
from typing import List
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class AcademicYear(Base):
    """
    Año Académico - Define el año lectivo (ej: 2026)
    Solo un año puede estar activo a la vez
    """
    __tablename__ = "academic_years"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    periods: Mapped[List["Period"]] = relationship("Period", back_populates="academic_year", cascade="all, delete-orphan")
    grades: Mapped[List["Grade"]] = relationship("Grade", back_populates="academic_year", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AcademicYear(year={self.year}, active={self.is_active})>"


class Period(Base):
    """
    Período académico - Trimestre, bimestre, etc.
    Pertenece a un año académico
    """
    __tablename__ = "periods"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", back_populates="periods")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('academic_year_id', 'name', name='unique_period_per_year'),
    )
    
    def __repr__(self):
        return f"<Period(name={self.name}, year={self.academic_year_id})>"


class Grade(Base):
    """
    Nivel o Grado académico - 7mo, 8vo, 9no, etc.
    Pertenece a un año académico
    """
    __tablename__ = "grades"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1-6 para primaria
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship("AcademicYear", back_populates="grades")
    groups: Mapped[List["Group"]] = relationship("Group", back_populates="grade", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('academic_year_id', 'level', name='unique_level_per_year'),
    )
    
    def __repr__(self):
        return f"<Grade(name={self.name}, level={self.level})>"


class Group(Base):
    """
    Grupo o Sección - Ej: "Sección A", "Grupo 1"
    Pertenece a un grado
    """
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grade: Mapped["Grade"] = relationship("Grade", back_populates="groups")
    subgroups: Mapped[List["Subgroup"]] = relationship("Subgroup", back_populates="group", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('grade_id', 'name', name='unique_group_per_grade'),
    )
    
    def __repr__(self):
        return f"<Group(name={self.name}, grade_id={self.grade_id})>"


class Subgroup(Base):
    """
    Subgrupo - Ej: "Grupo de trabajo 1", "Equipo A"
    Pertenece a un grupo/sección
    """
    __tablename__ = "subgroups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="subgroups")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="subgroup")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('group_id', 'name', name='unique_subgroup_per_group'),
    )
    
    def __repr__(self):
        return f"<Subgroup(name={self.name}, group_id={self.group_id})>"
