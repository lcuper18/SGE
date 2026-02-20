"""
Dependencias de permisos para SGE Grades MVP.

Uso en rutas:
    from app.dependencies import require_authenticated, require_admin_or_coordinator

    @router.get("/recurso")
    def listar(current_user: User = Depends(require_authenticated)):
        ...

    @router.post("/recurso")
    def crear(current_user: User = Depends(require_admin_or_coordinator)):
        ...
"""
from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.models.user import User, UserRole
from app.services.auth import get_current_user


def require_roles(*roles: UserRole) -> Callable:
    """
    Factory de dependencias: devuelve una dependencia FastAPI que
    valida que el usuario autenticado tenga uno de los roles indicados.

    Args:
        *roles: Roles permitidos (UserRole).

    Returns:
        Dependencia FastAPI que resuelve al objeto User si está autorizado,
        o lanza HTTP 403 si no tiene el rol necesario.
    """
    allowed_values = {r.value for r in roles}
    role_names = ", ".join(sorted(allowed_values))

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Roles requeridos: {role_names}",
            )
        return current_user

    return checker


# ---------------------------------------------------------------------------
# Atajos predefinidos (úsalos directamente en Depends())
# ---------------------------------------------------------------------------

require_admin = require_roles(UserRole.ADMIN)
"""Solo administradores."""

require_admin_or_coordinator = require_roles(UserRole.ADMIN, UserRole.COORDINATOR)
"""Administradores o coordinadores (lectura+escritura académica)."""

require_authenticated = require_roles(
    UserRole.ADMIN, UserRole.COORDINATOR, UserRole.TEACHER
)
"""Cualquier usuario de staff autenticado (lectura)."""
