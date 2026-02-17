"""
Modelo de usuario para SGE Grades MVP
Incluye autenticación con Argon2id
"""
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from passlib.context import CryptContext
from app.database import Base


# Configuración de Argon2id (NO bcrypt)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,         # 3 iterations
    argon2__parallelism=4        # 4 threads
)


class User(Base):
    """
    Usuario/Profesor del sistema
    Autenticación con Argon2id (secure password hashing)
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        """
        Hashea la contraseña con Argon2id y la guarda
        
        Args:
            password: Contraseña en texto plano
        """
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada coincide con el hash
        
        Args:
            password: Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False de lo contrario
        """
        return pwd_context.verify(password, self.password_hash)
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
