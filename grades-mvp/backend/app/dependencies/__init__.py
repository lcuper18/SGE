"""
Dependencies de FastAPI para el sistema SGE Grades MVP
"""
from app.dependencies.permissions import (
    require_roles,
    require_admin,
    require_admin_or_coordinator,
    require_authenticated,
)

__all__ = [
    "require_roles",
    "require_admin",
    "require_admin_or_coordinator",
    "require_authenticated",
]
