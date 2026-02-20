"""
Modelos de horarios para SGE Grades MVP
Define TimeSlot: bloques de lección, recreos y almuerzo por día y sección
Define TeacherGroupAssignment: asignación de profesor a grupo por materia y sección
"""
from datetime import datetime, time
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Time, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SlotType(str, PyEnum):
    """Tipo de bloque horario"""
    LESSON = "lesson"      # Bloque de clase
    BREAK = "break"        # Recreo
    LUNCH = "lunch"        # Almuerzo


class LessonType(str, PyEnum):
    """Tipo de lección (solo aplica cuando slot_type = lesson)"""
    ACADEMIC = "academic"    # Materias académicas — 40 min
    TECHNICAL = "technical"  # Materias técnicas — 60 min


class Section(str, PyEnum):
    """Sección / jornada escolar"""
    DAY = "day"      # Diurna (7:00 – 16:30)
    NIGHT = "night"  # Nocturna (18:00 – 22:00)


class Weekday(int, PyEnum):
    """Día de la semana (ISO: Monday = 0)"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


# Duración en minutos por tipo de lección
LESSON_DURATION_MINUTES = {
    LessonType.ACADEMIC: 40,
    LessonType.TECHNICAL: 60,
}

# Equivalencia: N lecciones técnicas = M lecciones académicas
# 4 técnicas = 6 académicas  →  1 técnica = 1.5 académicas
TECHNICAL_TO_ACADEMIC_RATIO = 1.5


class TimeSlot(Base):
    """
    Bloque horario — Representa una franja de tiempo dentro del día escolar.

    Un TimeSlot identifica:
    - Qué ocurre (lección, recreo, almuerzo)
    - En qué tipo de lección (académica, técnica) — solo si slot_type = lesson
    - En qué día de la semana (0 = lunes ... 6 = domingo)
    - En qué jornada (day = diurna, night = nocturna)
    - Horario exacto (start_time, end_time)

    Constraint: no pueden solaparse dos bloques del mismo weekday + section.
    """
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_type: Mapped[str] = mapped_column(String(20), nullable=False)
    lesson_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)   # 0–6 (Weekday enum)
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # day / night
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", "weekday", "section", name="unique_slot_name_per_day_section"),
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="check_weekday_range"),
        CheckConstraint(
            "slot_type IN ('lesson', 'break', 'lunch')",
            name="check_slot_type_values",
        ),
        CheckConstraint(
            "lesson_type IS NULL OR lesson_type IN ('academic', 'technical')",
            name="check_lesson_type_values",
        ),
        CheckConstraint(
            "section IN ('day', 'night')",
            name="check_section_values",
        ),
    )

    # ------------------------------------------------------------------
    # Propiedades calculadas
    # ------------------------------------------------------------------

    @property
    def duration_minutes(self) -> int:
        """Duración real del bloque en minutos."""
        start = self.start_time
        end = self.end_time
        return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)

    @property
    def academic_equivalent_minutes(self) -> float:
        """
        Minutos equivalentes académicos.
        - Hasta que lesson_type = 'technical': se multiplica por el ratio 1.5
        - Breaks y lunch: 0
        """
        if self.slot_type != SlotType.LESSON:
            return 0.0
        if self.lesson_type == LessonType.TECHNICAL:
            return self.duration_minutes * TECHNICAL_TO_ACADEMIC_RATIO
        return float(self.duration_minutes)

    def overlaps_with(self, other: "TimeSlot") -> bool:
        """
        Verifica si este bloque se solapa con otro del mismo weekday y section.
        Dos bloques se solapan si uno empieza antes de que termine el otro.
        """
        if self.weekday != other.weekday or self.section != other.section:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time

    def __repr__(self) -> str:
        return (
            f"<TimeSlot(name={self.name!r}, "
            f"weekday={self.weekday}, section={self.section!r}, "
            f"{self.start_time}–{self.end_time})>"
        )


class TeacherGroupAssignment(Base):
    """
    Asignación de Profesor a Grupo.

    Vincula un usuario con rol 'teacher' a un grupo (sección escolar) para una
    materia específica.  Esta tabla es la fuente de verdad para:
    - Determinar qué grupos puede ver un profesor en el módulo de asistencia.
    - Filtrar registros de asistencia por profesor autorizado.

    Un profesor puede estar asignado a:
    - Múltiples grupos (diferentes materias).
    - Un mismo grupo con varias materias (filas distintas con mismo group_id).

    Un grupo puede tener:
    - Múltiples profesores (uno por materia / bloque).

    Constraint de unicidad: un profesor no puede tener dos asignaciones
    con la misma combinación (group_id, subject, section).
    """
    __tablename__ = "teacher_group_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # FK al usuario con rol teacher (o coordinator que imparte)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # FK al grupo/sección
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Materia que imparte (ej. "Matemáticas", "Lengua y Literatura")
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    # Jornada: day | night
    section: Mapped[str] = mapped_column(String(10), nullable=False, default=Section.DAY.value)
    # FK opcional a período académico (si NULL aplica a todo el año)
    period_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("periods.id", ondelete="SET NULL"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id])
    group: Mapped["Group"] = relationship("Group", foreign_keys=[group_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "teacher_id", "group_id", "subject", "section",
            name="unique_teacher_group_subject_section",
        ),
        CheckConstraint(
            "section IN ('day', 'night')",
            name="check_assignment_section",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<TeacherGroupAssignment(teacher_id={self.teacher_id}, "
            f"group_id={self.group_id}, subject={self.subject!r}, "
            f"section={self.section!r})>"
        )
