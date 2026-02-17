# backend/app/database.py
"""
Database configuration with SQLCipher encryption
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import keyring

# Service name para keytar/keyring
SERVICE_NAME = "sge-grades-mvp"
ACCOUNT_NAME = "db-encryption-key"

def get_or_create_encryption_key() -> str:
    """
    Obtiene o crea la clave de encriptación de la base de datos.
    Almacenada en keychain del OS por seguridad.
    """
    try:
        key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        
        if not key:
            # Primera ejecución: generar clave aleatoria
            import secrets
            random_key = secrets.token_hex(32)  # 64 caracteres hex
            keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, random_key)
            print(f"[Database] Nueva clave de encriptación generada y guardada en keychain")
            return random_key
        
        return key
    
    except Exception as e:
        raise Exception(f"Error managing encryption key: {e}")


# Obtener clave de encriptación
ENCRYPTION_KEY = get_or_create_encryption_key()

# Database path
DB_DIR = os.path.expanduser("~/Documents/SGE-Grades")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "sge_grades.db")

# SQLCipher URL (mismo formato que SQLite)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine con SQLCipher
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Para SQLite
        "timeout": 30
    },
    poolclass=StaticPool,  # Single-user app
    echo=False  # True para debug
)

# Configurar SQLCipher en cada conexión
@event.listens_for(engine, "connect")
def configure_sqlite_connection(dbapi_connection, connection_record):
    """
    Configura SQLCipher y optimizaciones SQLite en cada conexión.
    """
    cursor = dbapi_connection.cursor()
    
    # 🔒 Activar encriptación SQLCipher
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}'")
    cursor.execute("PRAGMA cipher_page_size = 4096")
    cursor.execute("PRAGMA kdf_iter = 64000")
    
    # Optimizaciones SQLite
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA cache_size = 10000")
    cursor.execute("PRAGMA temp_store = MEMORY")
    
    cursor.close()
    print(f"[Database] Conexión SQLCipher configurada: {DB_PATH}")

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()

def get_db():
    """
    Dependency para obtener sesión de DB en endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa todas las tablas en la base de datos.
    Llamar después de importar todos los modelos.
    """
    from app import models  # Import all models
    Base.metadata.create_all(bind=engine)
    print("[Database] Tablas creadas exitosamente")


def test_encryption():
    """
    Verifica que SQLCipher esté funcionando correctamente.
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA cipher_version"))
            version = result.fetchone()
            
            if version and version[0]:
                print(f"[Database] SQLCipher versión: {version[0]}")
                print(f"[Database] ✅ Encriptación: ACTIVA")
                return True
            else:
                print(f"[Database] ⚠️  SQLite estándar detectado (SIN ENCRIPTACIÓN)")
                return False
    except Exception as e:
        print(f"[Database] Error verificando encriptación: {e}")
        print(f"[Database] ⚠️  No se pudo confirmar encriptación")
        return False
