"""
Servicio de negocio para TeacherGroupAssignment — Story 4.2
"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.academic import Group, Period
from app.models.schedule import TeacherGroupAssignment
from app.models.user import User
from app.schemas.teacher_assignments import (
    TeacherGroupAssignmentCreate,
    TeacherGroupAssignmentUpdate,
)


class TeacherAssignmentService:
    """Lógica de negocio para asignaciones profesor-grupo."""

    # ------------------------------------------------------------------
    # Validaciones privadas
    # ------------------------------------------------------------------

    @staticmethod
    def _get_teacher_or_404(db: Session, teacher_id: int) -> User:
        user = db.query(User).filter(User.id == teacher_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id={teacher_id} no encontrado",
            )
        if user.role not in ("teacher", "coordinator", "admin"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"El usuario '{user.username}' tiene rol '{user.role}'. "
                    "Solo teacher, coordinator o admin pueden ser asignados a grupos."
                ),
            )
        return user

    @staticmethod
    def _get_group_or_404(db: Session, group_id: int) -> Group:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo con id={group_id} no encontrado",
            )
        return group

    @staticmethod
    def _validate_period(db: Session, period_id: Optional[int]) -> None:
        if period_id is None:
            return
        period = db.query(Period).filter(Period.id == period_id).first()
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Período con id={period_id} no encontrado",
            )

    @staticmethod
    def _get_assignment_or_404(db: Session, assignment_id: int) -> TeacherGroupAssignment:
        assignment = (
            db.query(TeacherGroupAssignment)
            .filter(TeacherGroupAssignment.id == assignment_id)
            .first()
        )
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignación con id={assignment_id} no encontrada",
            )
        return assignment

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        db: Session, data: TeacherGroupAssignmentCreate
    ) -> TeacherGroupAssignment:
        """Crea una nueva asignación profesor-grupo."""
        TeacherAssignmentService._get_teacher_or_404(db, data.teacher_id)
        TeacherAssignmentService._get_group_or_404(db, data.group_id)
        TeacherAssignmentService._validate_period(db, data.period_id)

        assignment = TeacherGroupAssignment(
            teacher_id=data.teacher_id,
            group_id=data.group_id,
            subject=data.subject,
            section=data.section.value,
            period_id=data.period_id,
            is_active=data.is_active,
        )
        db.add(assignment)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Ya existe una asignación para teacher_id={data.teacher_id}, "
                    f"group_id={data.group_id}, subject='{data.subject}', "
                    f"section='{data.section.value}'."
                ),
            )
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_all(
        db: Session,
        teacher_id: Optional[int] = None,
        group_id: Optional[int] = None,
        section: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[TeacherGroupAssignment]:
        """Lista asignaciones con filtros opcionales."""
        query = db.query(TeacherGroupAssignment)
        if teacher_id is not None:
            query = query.filter(TeacherGroupAssignment.teacher_id == teacher_id)
        if group_id is not None:
            query = query.filter(TeacherGroupAssignment.group_id == group_id)
        if section is not None:
            query = query.filter(TeacherGroupAssignment.section == section)
        if is_active is not None:
            query = query.filter(TeacherGroupAssignment.is_active == is_active)
        return query.order_by(
            TeacherGroupAssignment.group_id,
            TeacherGroupAssignment.subject,
        ).all()

    @staticmethod
    def get_by_id(db: Session, assignment_id: int) -> TeacherGroupAssignment:
        return TeacherAssignmentService._get_assignment_or_404(db, assignment_id)

    @staticmethod
    def update(
        db: Session,
        assignment_id: int,
        data: TeacherGroupAssignmentUpdate,
    ) -> TeacherGroupAssignment:
        """Actualiza una asignación existente."""
        assignment = TeacherAssignmentService._get_assignment_or_404(db, assignment_id)

        if data.subject is not None:
            assignment.subject = data.subject
        if data.section is not None:
            assignment.section = data.section.value
        if data.period_id is not None:
            TeacherAssignmentService._validate_period(db, data.period_id)
            assignment.period_id = data.period_id
        if data.is_active is not None:
            assignment.is_active = data.is_active

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La actualización genera una asignación duplicada (teacher, group, subject, section).",
            )
        db.refresh(assignment)
        return assignment

    @staticmethod
    def delete(db: Session, assignment_id: int) -> None:
        """Elimina una asignación (hard delete)."""
        assignment = TeacherAssignmentService._get_assignment_or_404(db, assignment_id)
        db.delete(assignment)
        db.commit()

    # ------------------------------------------------------------------
    # Helper para construir el response con campos extra
    # ------------------------------------------------------------------

    @staticmethod
    def to_response_dict(assignment: TeacherGroupAssignment) -> dict:
        """Convierte el ORM object al dict que espera TeacherGroupAssignmentResponse."""
        return {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id,
            "group_id": assignment.group_id,
            "subject": assignment.subject,
            "section": assignment.section,
            "period_id": assignment.period_id,
            "is_active": assignment.is_active,
            "teacher_username": assignment.teacher.username,
            "teacher_full_name": assignment.teacher.full_name,
            "group_name": assignment.group.name,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
        }
