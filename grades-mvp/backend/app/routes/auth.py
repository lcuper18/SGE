"""
Rutas de autenticación para SGE Grades MVP
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slowapi.util import get_remote_address
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse,
    PasswordChange
)
from app.services.auth import (
    create_access_token,
    authenticate_user,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.limiter import limiter as app_limiter


# Router de autenticación
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@app_limiter.limit("3/minute")  # Máximo 3 registros por minuto
async def register(
    request: Request,
    user_data: UserRegister, 
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema
    
    - **username**: Username único (3-50 caracteres, alfanumérico)
    - **email**: Email único y válido
    - **password**: Contraseña segura (mín 8 caracteres, mayúscula, minúscula, número)
    - **full_name**: Nombre completo del usuario
    
    **Rate limit**: 3 registros por minuto por IP
    """
    # Verificar si username ya existe
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username ya está registrado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está registrado"
            )
    
    # Crear nuevo usuario
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        is_superuser=user_data.role == "admin"
    )
    
    # Hashear contraseña con Argon2id
    new_user.set_password(user_data.password)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            is_superuser=new_user.is_superuser,
            created_at=new_user.created_at.isoformat()
        )
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario. Verifica que username y email sean únicos."
        )


@router.post("/login", response_model=Token)
@app_limiter.limit("5/minute")  # Máximo 5 intentos por minuto
async def login(
    request: Request,
    credentials: UserLogin, 
    db: Session = Depends(get_db)
):
    """
    Inicia sesión y obtiene un token JWT
    
    - **username**: Username del usuario
    - **password**: Contraseña del usuario
    
    **Rate limit**: 5 intentos por minuto por IP
    
    **Returns**: Token JWT válido por 8 horas (480 minutos)
    """
    # Autenticar usuario
    user = authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # en segundos
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actualmente autenticado
    
    **Requiere**: Token JWT válido en header Authorization: Bearer <token>
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
@app_limiter.limit("3/hour")  # Máximo 3 cambios de contraseña por hora
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mín 8 caracteres, mayúscula, minúscula, número)
    
    **Rate limit**: 3 cambios por hora
    **Requiere**: Token JWT válido
    """
    # Verificar contraseña actual
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Establecer nueva contraseña
    current_user.set_password(password_data.new_password)
    
    try:
        db.commit()
        return {"message": "Contraseña actualizada exitosamente"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar contraseña"
        )
