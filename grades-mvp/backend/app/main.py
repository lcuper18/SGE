# backend/app/main.py
"""
FastAPI Application - SGE Grades MVP
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import init_db, test_encryption
from app.limiter import limiter
from app.routes import auth, academic_years, periods, grades, groups, students, time_slots, teacher_assignments

# FastAPI app
app = FastAPI(
    title="SGE Grades MVP API",
    description="API REST para módulo de calificaciones offline",
    version="1.0.0",
    docs_url="/docs" if __debug__ else None,  # Swagger solo en desarrollo
    redoc_url="/redoc" if __debug__ else None
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Solo localhost en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)


@app.on_event("startup")
async def startup_event():
    """
    Inicialización al arrancar la aplicación.
    """
    print("\n" + "="*50)
    print("🚀 SGE Grades MVP - Starting...")
    print("="*50)
    
    # Verificar encriptación SQLCipher
    if not test_encryption():
        print("⚠️  WARNING: SQLCipher no está funcionando correctamente")
    
    # Inicializar base de datos
    init_db()
    
    print("✅ Backend iniciado correctamente")
    print(f"📄 Documentación: http://localhost:8000/docs")
    print("="*50 + "\n")


@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "SGE Grades MVP API",
        "version": "1.0.0",
        "encryption": "SQLCipher AES-256"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check.
    """
    from app.database import engine
    from sqlalchemy import text
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "encryption": "active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


# ================== ROUTERS ==================

# Authentication routes
app.include_router(auth.router, prefix="/api")

# Academic structure routes
app.include_router(academic_years.router)
app.include_router(periods.router)
app.include_router(grades.router)
app.include_router(groups.router)
app.include_router(students.router)
app.include_router(time_slots.router)
app.include_router(teacher_assignments.router)


# TODO: Import additional routers cuando estén creados
# from app.routes import setup, students, attendance, grades, reports
# app.include_router(setup.router, prefix="/api/setup", tags=["Academic Setup"])
# etc...
