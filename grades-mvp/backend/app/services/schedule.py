"""
Servicio de horarios para SGE Grades MVP — Story 4.1
Lógica de negocio para TimeSlot: CRUD, validación de solapamiento y seed de plantillas
"""
from datetime import time
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.schedule import TimeSlot, SlotType, LessonType, Section, Weekday
from app.schemas.schedule import TimeSlotCreate, TimeSlotUpdate


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _times_overlap(s1: time, e1: time, s2: time, e2: time) -> bool:
    """True si el intervalo [s1, e1) se solapa con [s2, e2)."""
    return s1 < e2 and s2 < e1


def _check_overlap(
    db: Session,
    weekday: int,
    section: str,
    start_time: time,
    end_time: time,
    exclude_id: Optional[int] = None,
) -> None:
    """
    Lanza HTTP 409 si existe algún TimeSlot en el mismo weekday+section
    cuyo horario se solapa con [start_time, end_time).
    exclude_id se usa en updates para ignorar el slot que se está editando.
    """
    query = db.query(TimeSlot).filter(
        TimeSlot.weekday == weekday,
        TimeSlot.section == section,
        TimeSlot.is_active == True,
    )
    if exclude_id is not None:
        query = query.filter(TimeSlot.id != exclude_id)

    for existing in query.all():
        if _times_overlap(start_time, end_time, existing.start_time, existing.end_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"El bloque '{existing.name}' "
                    f"({existing.start_time.strftime('%H:%M')}–{existing.end_time.strftime('%H:%M')}) "
                    f"se solapa con el horario indicado."
                ),
            )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

class TimeSlotService:

    @staticmethod
    def create(db: Session, data: TimeSlotCreate) -> TimeSlot:
        """Crea un nuevo TimeSlot, validando solapamiento."""
        _check_overlap(
            db,
            weekday=data.weekday.value,
            section=data.section.value,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        slot = TimeSlot(
            name=data.name,
            start_time=data.start_time,
            end_time=data.end_time,
            slot_type=data.slot_type.value,
            lesson_type=data.lesson_type.value if data.lesson_type else None,
            weekday=data.weekday.value,
            section=data.section.value,
            is_active=data.is_active,
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        return slot

    @staticmethod
    def get_all(
        db: Session,
        weekday: Optional[int] = None,
        section: Optional[str] = None,
        slot_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[TimeSlot]:
        """
        Retorna todos los TimeSlots con filtros opcionales,
        ordenados por weekday → start_time.
        """
        q = db.query(TimeSlot)
        if weekday is not None:
            q = q.filter(TimeSlot.weekday == weekday)
        if section is not None:
            q = q.filter(TimeSlot.section == section)
        if slot_type is not None:
            q = q.filter(TimeSlot.slot_type == slot_type)
        if is_active is not None:
            q = q.filter(TimeSlot.is_active == is_active)
        return q.order_by(TimeSlot.weekday, TimeSlot.start_time).all()

    @staticmethod
    def get_by_id(db: Session, slot_id: int) -> Optional[TimeSlot]:
        return db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()

    @staticmethod
    def update(db: Session, slot_id: int, data: TimeSlotUpdate) -> TimeSlot:
        """Actualiza campos del TimeSlot, re-valida solapamiento si cambia horario."""
        slot = TimeSlotService.get_by_id(db, slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TimeSlot {slot_id} not found",
            )

        update_fields = data.model_dump(exclude_unset=True)

        # Resolución de valores finales para validar el solapamiento
        new_weekday = update_fields.get("weekday", slot.weekday)
        new_section = update_fields.get("section", slot.section)
        new_start = update_fields.get("start_time", slot.start_time)
        new_end = update_fields.get("end_time", slot.end_time)

        # Normalizar: los enums llegan como objetos, necesitamos el .value
        if hasattr(new_weekday, "value"):
            new_weekday = new_weekday.value
        if hasattr(new_section, "value"):
            new_section = new_section.value

        if new_end <= new_start:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="end_time debe ser posterior a start_time",
            )

        _check_overlap(db, new_weekday, new_section, new_start, new_end, exclude_id=slot_id)

        # Validar consistencia slot_type / lesson_type en la actualización
        final_slot_type = update_fields.get("slot_type", slot.slot_type)
        final_lesson_type = update_fields.get("lesson_type", slot.lesson_type)
        if hasattr(final_slot_type, "value"):
            final_slot_type = final_slot_type.value
        if hasattr(final_lesson_type, "value"):
            final_lesson_type = final_lesson_type.value

        if final_slot_type == SlotType.LESSON.value and final_lesson_type is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="lesson_type es requerido cuando slot_type es 'lesson'",
            )
        if final_slot_type != SlotType.LESSON.value and final_lesson_type is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="lesson_type solo aplica cuando slot_type es 'lesson'",
            )

        # Aplicar cambios
        for field, value in update_fields.items():
            setattr(slot, field, value.value if hasattr(value, "value") else value)

        db.commit()
        db.refresh(slot)
        return slot

    @staticmethod
    def delete(db: Session, slot_id: int) -> None:
        """Elimina permanentemente un TimeSlot."""
        slot = TimeSlotService.get_by_id(db, slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TimeSlot {slot_id} not found",
            )
        db.delete(slot)
        db.commit()

    # ------------------------------------------------------------------
    # Seed de plantillas por defecto
    # ------------------------------------------------------------------

    @staticmethod
    def seed_template(
        db: Session,
        section: str,
        weekdays: List[int],
        overwrite: bool = False,
    ) -> dict:
        """
        Genera los bloques horarios estándar para la sección indicada.

        Plantilla diurna (day):
          07:00 – 07:40  Bloque 1 (academic)
          07:40 – 08:20  Bloque 2 (academic)
          08:20 – 09:00  Bloque 3 (academic)
          09:00 – 09:20  Recreo   (break)
          09:20 – 10:00  Bloque 4 (academic)
          10:00 – 10:40  Bloque 5 (academic)
          10:40 – 11:20  Bloque 6 (academic)
          11:20 – 12:20  Almuerzo (lunch)
          12:20 – 13:20  Bloque 7 (technical)
          13:20 – 14:20  Bloque 8 (technical)
          14:20 – 14:40  Recreo 2 (break)
          14:40 – 15:40  Bloque 9 (technical)
          15:40 – 16:40  Bloque 10 (technical)

        Plantilla nocturna (night):
          18:00 – 19:00  Bloque 1 (technical)
          19:00 – 20:00  Bloque 2 (technical)
          20:00 – 20:20  Recreo   (break)
          20:20 – 21:20  Bloque 3 (technical)
          21:20 – 22:00  Bloque 4 (academic)
        """
        if section == Section.DAY.value:
            template = [
                ("Bloque 1",  time(7, 0),  time(7, 40),  SlotType.LESSON, LessonType.ACADEMIC),
                ("Bloque 2",  time(7, 40), time(8, 20),  SlotType.LESSON, LessonType.ACADEMIC),
                ("Bloque 3",  time(8, 20), time(9, 0),   SlotType.LESSON, LessonType.ACADEMIC),
                ("Recreo",    time(9, 0),  time(9, 20),  SlotType.BREAK,  None),
                ("Bloque 4",  time(9, 20), time(10, 0),  SlotType.LESSON, LessonType.ACADEMIC),
                ("Bloque 5",  time(10, 0), time(10, 40), SlotType.LESSON, LessonType.ACADEMIC),
                ("Bloque 6",  time(10, 40),time(11, 20), SlotType.LESSON, LessonType.ACADEMIC),
                ("Almuerzo",  time(11, 20),time(12, 20), SlotType.LUNCH,  None),
                ("Bloque 7",  time(12, 20),time(13, 20), SlotType.LESSON, LessonType.TECHNICAL),
                ("Bloque 8",  time(13, 20),time(14, 20), SlotType.LESSON, LessonType.TECHNICAL),
                ("Recreo 2",  time(14, 20),time(14, 40), SlotType.BREAK,  None),
                ("Bloque 9",  time(14, 40),time(15, 40), SlotType.LESSON, LessonType.TECHNICAL),
                ("Bloque 10", time(15, 40),time(16, 40), SlotType.LESSON, LessonType.TECHNICAL),
            ]
        else:  # night
            template = [
                ("Bloque 1", time(18, 0),  time(19, 0),  SlotType.LESSON, LessonType.TECHNICAL),
                ("Bloque 2", time(19, 0),  time(20, 0),  SlotType.LESSON, LessonType.TECHNICAL),
                ("Recreo",   time(20, 0),  time(20, 20), SlotType.BREAK,  None),
                ("Bloque 3", time(20, 20), time(21, 20), SlotType.LESSON, LessonType.TECHNICAL),
                ("Bloque 4", time(21, 20), time(22, 0),  SlotType.LESSON, LessonType.ACADEMIC),
            ]

        created = 0
        skipped = 0
        overwritten = 0

        for day in weekdays:
            for name, start, end, s_type, l_type in template:
                # Verificar si ya existe (por nombre + día + sección)
                exists = db.query(TimeSlot).filter(
                    TimeSlot.name == name,
                    TimeSlot.weekday == day,
                    TimeSlot.section == section,
                ).first()

                if exists:
                    if overwrite:
                        db.delete(exists)
                        db.flush()
                        overwritten += 1
                    else:
                        skipped += 1
                        continue
                else:
                    created += 1

                slot = TimeSlot(
                    name=name,
                    start_time=start,
                    end_time=end,
                    slot_type=s_type.value,
                    lesson_type=l_type.value if l_type else None,
                    weekday=day,
                    section=section,
                    is_active=True,
                )
                db.add(slot)

        db.commit()
        return {"created": created, "skipped": skipped, "overwritten": overwritten}
