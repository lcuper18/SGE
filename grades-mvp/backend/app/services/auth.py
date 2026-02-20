"""
Servicio de autenticación con JWT y Argon2id
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData


# Configuración JWT desde .env
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

# Security scheme para Bearer token
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados
    
    Args:
        data: Diccionario con datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # issued at
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decodifica y valida un token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        TokenData con información del usuario, o None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if subject is None:
            return None
        
        user_id = int(subject)  # sub siempre se almacena como string en JWT
        return TokenData(user_id=user_id, username=username, role=role)
    
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales Bearer con token JWT
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar token
    token_data = decode_access_token(credentials.credentials)
    
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    # Buscar usuario en BD
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para verificar que el usuario actual es superusuario
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Usuario si es superusuario
        
    Raises:
        HTTPException 403: Si el usuario no es superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene suficientes permisos"
        )
    return current_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Autentica un usuario con username y password
    
    Args:
        db: Sesión de base de datos
        username: Username del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si la autenticación es exitosa, None si falla
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    if not user.is_active:
        return None
    
    return user
