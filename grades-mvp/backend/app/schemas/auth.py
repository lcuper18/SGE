"""
Schemas de autenticación para SGE Grades MVP
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegister(BaseModel):
    """Schema para registro de nuevo usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=200)
    
    @validator('username')
    def validate_username(cls, v):
        """Validar formato de username"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validar seguridad de contraseña"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Contraseña debe contener al menos un número')
        return v


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class Token(BaseModel):
    """Schema de respuesta con token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos hasta expiración


class TokenData(BaseModel):
    """Datos decodificados del token JWT"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    """Schema de respuesta con datos de usuario (sin password)"""
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: str
    
    class Config:
        from_attributes = True  # SQLAlchemy compatibility (antes orm_mode)


class PasswordChange(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validar nueva contraseña"""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('Nueva contraseña debe ser diferente a la actual')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Contraseña debe contener al menos un número')
        return v
