"""
Modelo de estudiante para SGE Grades MVP
"""
from datetime import datetime, date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class Student(Base):
    """
    Estudiante del sistema
    Pertenece a un subgrupo dentro de la estructura académica
    """
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    identification: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    subgroup_id: Mapped[int] = mapped_column(ForeignKey("subgroups.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subgroup: Mapped["Subgroup"] = relationship("Subgroup", back_populates="students")
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del estudiante"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Student(id={self.identification}, name={self.full_name})>"
