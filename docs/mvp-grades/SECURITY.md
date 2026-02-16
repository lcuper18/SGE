# Seguridad - MVP Módulo de Calificaciones

## 🎯 Principios de Seguridad

**Contexto crítico:** Este sistema maneja datos educativos sensibles de menores de edad (notas, asistencia, datos personales). La seguridad NO es opcional.

**Principios fundamentales:**
1. **Security by Design** - Seguridad desde Sprint 0, no después
2. **Defense in Depth** - Múltiples capas de protección
3. **Least Privilege** - Mínimos permisos necesarios
4. **Data Encryption** - Datos sensibles siempre encriptados
5. **Audit Trail** - Todo cambio es rastreable

---

## 🔒 Medidas de Seguridad Implementadas

### 1. Electron Security Hardening (Sprint 0)

**Configuración obligatoria:**

```javascript
// electron/main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      // SEGURIDAD CRÍTICA
      nodeIntegration: false,           // ✅ Previene RCE desde renderer
      contextIsolation: true,            // ✅ Aísla mundo de Electron del mundo web
      enableRemoteModule: false,         // ✅ Remote module = vulnerabilidad
      sandbox: true,                     // ✅ Sandbox adicional para renderer
      preload: path.join(__dirname, 'preload.js'),
      
      // NO permitir eval ni nuevas ventanas inseguras
      webSecurity: true,
      allowRunningInsecureContent: false,
      experimentalFeatures: false
    }
  });
  
  // Content Security Policy estricta
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; " +
          "script-src 'self'; " +
          "style-src 'self' 'unsafe-inline'; " +  // Tailwind requiere inline
          "img-src 'self' data:; " +
          "connect-src 'self' http://localhost:8000; " +  // FastAPI local
          "font-src 'self'; " +
          "object-src 'none'; " +
          "base-uri 'self'; " +
          "form-action 'self'"
        ]
      }
    });
  });
  
  // Prevenir navegación a sitios externos
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    if (parsedUrl.origin !== 'file://' && parsedUrl.origin !== 'http://localhost:3000') {
      event.preventDefault();
      console.warn('Navigation blocked:', navigationUrl);
    }
  });
  
  // Bloquear apertura de nuevas ventanas
  mainWindow.webContents.setWindowOpenHandler(() => {
    return { action: 'deny' };
  });
  
  mainWindow.loadURL('http://localhost:3000');  // Dev
  // mainWindow.loadFile('build/index.html');    // Production
}

app.whenReady().then(createWindow);
```

**Preload.js seguro:**

```javascript
// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Solo exponer APIs específicas y validadas
contextBridge.exposeInMainWorld('electron', {
  // Almacenamiento seguro de tokens
  storeToken: (token) => ipcRenderer.invoke('store-token-secure', token),
  getToken: () => ipcRenderer.invoke('get-token-secure'),
  removeToken: () => ipcRenderer.invoke('remove-token-secure'),
  
  // Operaciones de archivo seguras
  exportPDF: (data) => ipcRenderer.invoke('export-pdf', data),
  selectFile: () => ipcRenderer.invoke('select-file-dialog'),
  
  // Sistema de notificaciones
  showNotification: (title, body) => ipcRenderer.send('show-notification', { title, body })
});

// NO exponer: require, process, file system directo, child_process
```

**Main process con keychain del OS:**

```javascript
// electron/main.js - IPC handlers seguros
const keytar = require('keytar');

const SERVICE_NAME = 'sge-grades-mvp';
const ACCOUNT_NAME = 'jwt-token';

ipcMain.handle('store-token-secure', async (event, token) => {
  try {
    await keytar.setPassword(SERVICE_NAME, ACCOUNT_NAME, token);
    return { success: true };
  } catch (error) {
    console.error('Error storing token:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-token-secure', async () => {
  try {
    const token = await keytar.getPassword(SERVICE_NAME, ACCOUNT_NAME);
    return { success: true, token };
  } catch (error) {
    console.error('Error retrieving token:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('remove-token-secure', async () => {
  try {
    await keytar.deletePassword(SERVICE_NAME, ACCOUNT_NAME);
    return { success: true };
  } catch (error) {
    console.error('Error removing token:', error);
    return { success: false, error: error.message };
  }
});
```

---

### 2. Base de Datos Encriptada con SQLCipher (Sprint 0)

**SQLCipher en lugar de SQLite estándar:**

```python
# backend/app/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

# Ubicación segura de la base de datos
DB_DIR = Path.home() / "Documents" / "SGE-Grades"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "sge_grades.db"

# Key de encriptación (derivada de password del usuario)
# Se genera en primera ejecución y se guarda en OS keychain
ENCRYPTION_KEY = get_or_create_encryption_key()  # Implementar con keytar

# SQLCipher URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine con SQLCipher
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    echo=False
)

# Configurar SQLCipher en cada conexión
@event.listens_for(engine, "connect")
def configure_sqlite_connection(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    
    # Activar encriptación SQLCipher
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}'")
    cursor.execute("PRAGMA cipher_page_size = 4096")
    cursor.execute("PRAGMA kdf_iter = 256000")  # PBKDF2 iterations
    cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
    cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")
    
    # Optimizaciones SQLite
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA cache_size = 10000")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.close()

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Gestión de clave de encriptación:**

```python
# backend/app/services/encryption_service.py
import keyring
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

SERVICE_NAME = "sge-grades-mvp"
ACCOUNT_NAME = "db-encryption-key"

def get_or_create_encryption_key() -> str:
    """
    Obtiene o crea la clave de encriptación de la base de datos.
    La clave se deriva del password del usuario con PBKDF2.
    """
    try:
        # Intentar recuperar clave existente del OS keychain
        key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
        
        if key:
            return key
        
        # Si no existe, generar nueva clave segura
        # Nota: En primera ejecución, se derivará del password del usuario
        # Por ahora, generamos una clave aleatoria
        random_key = secrets.token_hex(32)  # 256 bits
        
        # Guardar en keychain del OS
        keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, random_key)
        
        return random_key
        
    except Exception as e:
        raise Exception(f"Error managing encryption key: {e}")

def derive_key_from_password(password: str, salt: bytes) -> str:
    """
    Deriva una clave de encriptación desde el password del usuario.
    Usado en primera configuración.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2024
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode())
    return base64.b64encode(key).decode()
```

**Primera configuración con password:**

```python
# backend/app/routes/auth.py
from app.services.encryption_service import derive_key_from_password
import keyring
import secrets

@router.post("/auth/initial-setup")
async def initial_setup(data: InitialSetupSchema):
    """
    Primera configuración del sistema.
    Deriva la clave de encriptación del password del usuario.
    """
    db = SessionLocal()
    
    # Verificar que no existan usuarios
    if db.query(User).count() > 0:
        raise HTTPException(400, "Setup already completed")
    
    # Generar salt único para esta instalación
    salt = secrets.token_bytes(32)
    
    # Derivar clave de encriptación desde password
    encryption_key = derive_key_from_password(data.password, salt)
    
    # Guardar clave en OS keychain
    keyring.set_password("sge-grades-mvp", "db-encryption-key", encryption_key)
    keyring.set_password("sge-grades-mvp", "db-salt", salt.hex())
    
    # Ahora crear tablas con SQLCipher usando esta clave
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role='teacher',
        teacher_type=data.teacher_type
    )
    db.add(user)
    db.commit()
    
    token = create_access_token({"user_id": user.id})
    
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}"
        },
        "security": {
            "database_encrypted": True,
            "algorithm": "SQLCipher AES-256"
        }
    }
```

---

### 3. Autenticación Segura (Sprint 0)

**Password hashing con Argon2id:**

```python
# backend/app/services/auth_service.py
from passlib.context import CryptContext

# Argon2id es el estándar actual (mejor que bcrypt)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,      # 64 MB
    argon2__time_cost=3,            # 3 iterations
    argon2__parallelism=4           # 4 threads
)

def hash_password(password: str) -> str:
    """Hash de password con Argon2id"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return pwd_context.verify(plain_password, hashed_password)
```

**Política de contraseñas fuertes:**

```python
# backend/app/services/password_validator.py
import re
from typing import List, Tuple

# Lista de passwords comunes más usados (cargar de archivo)
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    # ... top 10,000 de lista HIBP
}

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Valida fortaleza de password según políticas institucionales.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Longitud mínima
    if len(password) < 12:
        errors.append("Password debe tener al menos 12 caracteres")
    
    # Al menos una mayúscula
    if not re.search(r'[A-Z]', password):
        errors.append("Debe contener al menos una letra mayúscula")
    
    # Al menos una minúscula
    if not re.search(r'[a-z]', password):
        errors.append("Debe contener al menos una letra minúscula")
    
    # Al menos un número
    if not re.search(r'\d', password):
        errors.append("Debe contener al menos un número")
    
    # Al menos un símbolo
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Debe contener al menos un símbolo especial")
    
    # No está en lista de passwords comunes
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Este password es muy común. Elige uno más seguro")
    
    return (len(errors) == 0, errors)
```

**Rate limiting de login:**

```python
# backend/app/middleware/rate_limiter.py
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import HTTPException
from app.database import SessionLocal
from app.models import LoginAttempt

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

class RateLimiter:
    def __init__(self):
        self.attempts = defaultdict(list)
    
    def check_rate_limit(self, email: str):
        """
        Verifica si el usuario ha excedido intentos de login.
        Persiste en DB para sobrevivir restart de app.
        """
        db = SessionLocal()
        
        # Obtener intentos recientes desde DB
        cutoff = datetime.utcnow() - timedelta(minutes=LOCKOUT_MINUTES)
        recent_attempts = db.query(LoginAttempt).filter(
            LoginAttempt.email == email,
            LoginAttempt.attempted_at > cutoff,
            LoginAttempt.success == False
        ).count()
        
        if recent_attempts >= MAX_ATTEMPTS:
            # Calcular tiempo restante de bloqueo
            oldest_attempt = db.query(LoginAttempt).filter(
                LoginAttempt.email == email,
                LoginAttempt.attempted_at > cutoff
            ).order_by(LoginAttempt.attempted_at.asc()).first()
            
            unlock_time = oldest_attempt.attempted_at + timedelta(minutes=LOCKOUT_MINUTES)
            seconds_left = (unlock_time - datetime.utcnow()).total_seconds()
            minutes_left = int(seconds_left / 60) + 1
            
            raise HTTPException(
                status_code=429,
                detail=f"Demasiados intentos fallidos. Intenta de nuevo en {minutes_left} minutos"
            )
        
        db.close()
    
    def record_attempt(self, email: str, success: bool, ip_address: str = None):
        """Registra intento de login en DB"""
        db = SessionLocal()
        
        attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=ip_address,
            attempted_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        db.close()
    
    def reset_attempts(self, email: str):
        """Resetea intentos después de login exitoso"""
        db = SessionLocal()
        
        # Marcar intentos antiguos como resueltos
        db.query(LoginAttempt).filter(
            LoginAttempt.email == email,
            LoginAttempt.success == False
        ).update({"resolved": True})
        
        db.commit()
        db.close()

rate_limiter = RateLimiter()
```

**Aplicar en login endpoint:**

```python
# backend/app/routes/auth.py
from app.middleware.rate_limiter import rate_limiter
from app.services.password_validator import validate_password_strength

@router.post("/auth/register")
async def register(data: RegisterSchema):
    """Registro con validación de password fuerte"""
    
    # Validar fortaleza de password
    is_valid, errors = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(400, {"message": "Password débil", "errors": errors})
    
    # Continuar con registro...
    
@router.post("/auth/login")
async def login(credentials: LoginSchema, request: Request):
    """Login con rate limiting"""
    
    # Check rate limit
    rate_limiter.check_rate_limit(credentials.email)
    
    db = SessionLocal()
    user = db.query(User).filter_by(email=credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        # Registrar intento fallido
        rate_limiter.record_attempt(
            credentials.email,
            success=False,
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(401, "Credenciales inválidas")
    
    # Login exitoso - resetear contador
    rate_limiter.reset_attempts(credentials.email)
    rate_limiter.record_attempt(credentials.email, success=True)
    
    token = create_access_token({"user_id": user.id})
    
    return {"access_token": token, "user": {...}}
```

---

### 4. Protección contra XSS (Sprint 1)

**Frontend - Sanitización de inputs:**

```typescript
// frontend/src/utils/sanitize.ts
import DOMPurify from 'dompurify';

export const sanitizeHTML = (dirty: string): string => {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'br'],
    ALLOWED_ATTR: []
  });
};

export const sanitizeText = (text: string): string => {
  // Remover caracteres peligrosos
  return text.replace(/[<>]/g, '');
};

// Hook React para sanitizar inputs
export const useSanitizedInput = (initialValue: string = '') => {
  const [value, setValue] = useState(initialValue);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const sanitized = sanitizeText(e.target.value);
    setValue(sanitized);
  };
  
  return [value, handleChange] as const;
};
```

**Uso en componentes:**

```typescript
// frontend/src/components/StudentForm.tsx
import { useSanitizedInput } from '@/utils/sanitize';

export function StudentForm() {
  const [firstName, handleFirstNameChange] = useSanitizedInput();
  const [lastName, handleLastNameChange] = useSanitizedInput();
  
  return (
    <form>
      <input 
        value={firstName}
        onChange={handleFirstNameChange}  // Auto-sanitiza
        placeholder="Nombre"
      />
      <input 
        value={lastName}
        onChange={handleLastNameChange}
        placeholder="Apellido"
      />
    </form>
  );
}
```

---

### 5. Logging de Auditoría (Sprint 2)

**Modelo de auditoría:**

```python
# backend/app/models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)  # 'create_grade', 'update_attendance', etc.
    entity_type = Column(String(50), nullable=False)  # 'student', 'grade', 'attendance'
    entity_id = Column(Integer, nullable=False)
    old_value = Column(JSON, nullable=True)  # Estado anterior
    new_value = Column(JSON, nullable=True)  # Estado nuevo
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>"
```

**Servicio de auditoría:**

```python
# backend/app/services/audit_service.py
from app.models import AuditLog
from app.database import SessionLocal
from datetime import datetime

class AuditService:
    @staticmethod
    def log(
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_value: dict = None,
        new_value: dict = None,
        ip_address: str = None
    ):
        """Registra una acción en el audit log"""
        db = SessionLocal()
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        db.add(log)
        db.commit()
        db.close()
    
    @staticmethod
    def get_entity_history(entity_type: str, entity_id: int):
        """Obtiene historial de cambios de una entidad"""
        db = SessionLocal()
        
        history = db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(AuditLog.timestamp.desc()).all()
        
        db.close()
        return history
```

**Uso en endpoints:**

```python
# backend/app/routes/grades.py
from app.services.audit_service import AuditService

@router.post("/grades/save")
async def save_grade(
    grade_data: GradeCreateSchema,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    
    # Verificar si existe grade previo
    existing = db.query(GradeRecord).filter_by(
        student_id=grade_data.student_id,
        assignment_id=grade_data.assignment_id
    ).first()
    
    old_value = existing.to_dict() if existing else None
    
    # Guardar nueva grade
    if existing:
        existing.points_earned = grade_data.points_earned
        grade = existing
    else:
        grade = GradeRecord(**grade_data.dict())
        db.add(grade)
    
    db.commit()
    
    # Auditar cambio
    AuditService.log(
        user_id=current_user.id,
        action='update_grade' if existing else 'create_grade',
        entity_type='grade',
        entity_id=grade.id,
        old_value=old_value,
        new_value=grade.to_dict()
    )
    
    return {"success": True, "grade": grade.to_dict()}
```

---

### 6. Backups Automáticos Encriptados (Sprint 3)

```python
# backend/app/services/backup_service.py
import shutil
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
import keyring

BACKUP_DIR = Path.home() / "Documents" / "SGE-Backups"
BACKUP_DIR.mkdir(exist_ok=True)

class BackupService:
    def __init__(self):
        self.db_path = Path.home() / "Documents" / "SGE-Grades" / "sge_grades.db"
        self.backup_dir = BACKUP_DIR
        
    def create_backup(self):
        """Crea backup encriptado de la base de datos"""
        if not self.db_path.exists():
            raise FileNotFoundError("Database not found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"sge_grades_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        # Copiar DB (ya está encriptada con SQLCipher)
        shutil.copy2(self.db_path, backup_path)
        
        # Mantener solo últimos 30 backups
        self._cleanup_old_backups()
        
        return backup_path
    
    def _cleanup_old_backups(self):
        """Mantiene solo los últimos 30 backups"""
        backups = sorted(
            self.backup_dir.glob("sge_grades_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Eliminar backups antiguos
        for old_backup in backups[30:]:
            old_backup.unlink()
    
    def restore_backup(self, backup_path: Path):
        """Restaura desde un backup"""
        if not backup_path.exists():
            raise FileNotFoundError("Backup not found")
        
        # Crear backup del estado actual antes de restaurar
        self.create_backup()
        
        # Restaurar
        shutil.copy2(backup_path, self.db_path)
        
        return True

# Programar backup automático diario
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
backup_service = BackupService()

scheduler.add_job(
    backup_service.create_backup,
    'cron',
    hour=23,
    minute=0,  # Todos los días a las 11 PM
    id='daily_backup'
)

scheduler.start()
```

---

## 🔍 Auditoría de Seguridad Pre-Launch

### Checklist de seguridad antes de lanzar:

- [ ] **Electron hardened**
  - [ ] `nodeIntegration: false`
  - [ ] `contextIsolation: true`
  - [ ] CSP configurado
  - [ ] Navigation bloqueada

- [ ] **Base de datos**
  - [ ] SQLCipher implementado y testeado
  - [ ] Key management con keychain del OS
  - [ ] Backups automáticos funcionando

- [ ] **Autenticación**
  - [ ] Argon2id para passwords
  - [ ] Política de contraseñas fuertes
  - [ ] Rate limiting activo
  - [ ] Tokens en keychain (no localStorage)

- [ ] **Input validation**
  - [ ] Pydantic schemas en todos los endpoints
  - [ ] DOMPurify en frontend
  - [ ] Sanitización de CSV imports

- [ ] **Auditoría**
  - [ ] Audit logs funcionando
  - [ ] Login attempts registrados
  - [ ] Grade changes rastreables

- [ ] **Updates**
  - [ ] Auto-updater con verificación de firma
  - [ ] HTTPS para downloads
  - [ ] Rollback mechanism

- [ ] **Testing**
  - [ ] Pentesting básico realizado
  - [ ] SQL injection tests (negativos)
  - [ ] XSS tests (negativos)
  - [ ] Rate limiting verificado

---

## 📚 Recursos y Referencias

- [Electron Security Checklist](https://www.electronjs.org/docs/latest/tutorial/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SQLCipher Documentation](https://www.zetetic.net/sqlcipher/documentation/)
- [Argon2 Spec](https://github.com/P-H-C/phc-winner-argon2)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)

---

**Última actualización:** 16 de febrero, 2026  
**Próxima revisión:** Post-Sprint 6 (security audit)
