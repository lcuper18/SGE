# Plan de Trabajo - Próxima Sesión

**Fecha Objetivo**: 18-24 febrero 2026  
**Sprint**: Sprint 0 (finalización) + Sprint 1 (inicio)  
**Prioridad**: Completar fundamentos antes de features

---

## 🎯 Objetivos Principales

### 1. Completar Sprint 0 (Prioridad CRÍTICA)
**Tiempo estimado**: 2-3 horas

#### A. Resolver SQLCipher en Linux
**Problema**: `pysqlcipher3` no está funcionando (usando SQLite estándar)

**Opciones**:

**Opción A: Instalación Sistema** (Recomendado)
```bash
# 1. Instalar dependencias del sistema
sudo apt install sqlcipher libsqlcipher-dev python3-dev

# 2. Reinstalar pysqlcipher3 con compilación
cd /home/lfallas/Workspace/SGE/grades-mvp/backend
source venv/bin/activate
pip uninstall pysqlcipher3
pip install --no-binary :all: pysqlcipher3

# 3. Verificar instalación
python -c "from pysqlcipher3 import dbapi2; print('✅ SQLCipher OK')"
```

**Opción B: Usar sqlcipher3-binary** (Alternativa)
```bash
pip install sqlcipher3-binary
# Cambiar imports en database.py
```

**Opción C: Docker** (Si A y B fallan)
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y sqlcipher libsqlcipher-dev
# ...
```

**Validación**:
- [ ] Test de encriptación real funcionando
- [ ] DB creada en `~/Documents/SGE-Grades/sge_grades.db`
- [ ] PRAGMA cipher_version retorna versión SQLCipher

---

### 2. Crear Modelos de Base de Datos (Prioridad ALTA)
**Tiempo estimado**: 3-4 horas

#### A. Implementar User Model con Argon2id
**Archivo**: `backend/app/models/user.py`

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from passlib.context import CryptContext
from app.database import Base

# Argon2id context (NO bcrypt)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=1
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default='teacher')
    teacher_type = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def set_password(self, password: str):
        """Hash password con Argon2id"""
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verificar password"""
        return pwd_context.verify(password, self.password_hash)
    
    def __repr__(self):
        return f"<User {self.email}>"
```

**Tareas**:
- [ ] Crear `models/user.py`
- [ ] Agregar import en `models/__init__.py`
- [ ] Probar hash/verify con Argon2id
- [ ] Validar que bcrypt NO funciona

#### B. Crear Academic Structure Models
**Archivo**: `backend/app/models/academic.py`

```python
# 5 tablas: AcademicYear, Period, Grade, Group, Subgroup
# Según DATABASE.md líneas 81-230
```

**Tareas**:
- [ ] Crear `models/academic.py`
- [ ] Implementar 5 modelos SQLAlchemy
- [ ] Agregar relationships
- [ ] Validaciones (check constraints)

#### C. Crear Student Model
**Archivo**: `backend/app/models/student.py`

```python
# 1 tabla: Student
# Según DATABASE.md líneas 231-267
```

**Tareas**:
- [ ] Crear `models/student.py`
- [ ] Relationships con Group/Subgroup
- [ ] Index en student_id (único)

#### D. Inicializar Base de Datos
**Tareas**:
- [ ] Ejecutar `init_db()` desde main.py startup
- [ ] Verificar que 7 tablas se crean
- [ ] Confirmar encriptación SQLCipher activa

---

### 3. Implementar Autenticación (Prioridad ALTA)
**Tiempo estimado**: 2-3 horas

#### A. Password Validator Service
**Archivo**: `backend/app/services/password_validator.py`

```python
# Validaciones según ROADMAP.md Sprint 0
# - Min 12 caracteres
# - Mayúscula, número, símbolo
# - Lista de passwords comunes rechazados
```

**Tareas**:
- [ ] Crear password_validator.py
- [ ] Lista top 10K passwords comunes
- [ ] Tests de validación

#### B. Rate Limiter Class
**Archivo**: `backend/app/services/rate_limiter.py`

```python
# Tabla login_attempts en DB
# Max 5 intentos / 15 minutos
# Lockout automático
```

**Tareas**:
- [ ] Crear rate_limiter.py
- [ ] Modelo LoginAttempt
- [ ] Cleanup automático (TTL)

#### C. Auth Routes
**Archivo**: `backend/app/routes/auth.py`

```python
# POST /auth/initial-setup - Primera configuración
# POST /auth/login - Login con rate limit
# POST /auth/logout - Logout
# GET /auth/me - Usuario actual
```

**Tareas**:
- [ ] Crear routes/auth.py
- [ ] JWT token generation
- [ ] Middleware autenticación
- [ ] Dependency get_current_user

---

### 4. Setup Testing Framework (Prioridad MEDIA)
**Tiempo estimado**: 1-2 horas

#### A. Backend Testing (pytest)
**Archivos**:
- `backend/pytest.ini`
- `backend/conftest.py`
- `backend/tests/test_database.py`
- `backend/tests/test_auth.py`

**Tareas**:
- [ ] Configurar pytest
- [ ] Factory fixtures para User
- [ ] Test DB en memoria (SQLite)
- [ ] Tests básicos (5+)

#### B. Frontend Testing (Jest)
**Archivos**:
- `frontend/jest.config.js`
- `frontend/src/services/__tests__/api.test.ts`

**Tareas**:
- [ ] Configurar Jest + Testing Library
- [ ] Tests de API service
- [ ] Mock axios

---

## 📋 Checklist de Entregables

### Sprint 0 Completado ✅
- [ ] SQLCipher funcionando (encriptación real)
- [ ] 7 modelos creados (User + Academic + Student)
- [ ] Argon2id implementado y testeado
- [ ] Rate limiting en login funcional
- [ ] 25+ tests passing
- [ ] Coverage > 70%

### Criterios de Aceptación
1. ✅ `pytest` ejecuta sin errores
2. ✅ Test de encriptación DB pasa
3. ✅ Test de Argon2id rechaza bcrypt
4. ✅ Test de rate limiting bloquea 6to intento
5. ✅ Estructura de 7 tablas creada en DB

---

## 🔄 Orden de Ejecución Recomendado

### Sesión 1 (2-3 horas)
1. **Resolver SQLCipher** (30 min)
   - Opción A → B → C hasta que funcione
   
2. **Crear User Model** (45 min)
   - Con Argon2id
   - Tests básicos

3. **Crear Academic Models** (60 min)
   - 5 modelos
   - Relationships

4. **Inicializar DB** (15 min)
   - Ejecutar migrations
   - Verificar tablas

### Sesión 2 (2-3 horas)
5. **Password Validator** (30 min)
   - Service + tests

6. **Rate Limiter** (45 min)
   - Service + modelo LoginAttempt

7. **Auth Routes** (60 min)
   - 4 endpoints
   - JWT middleware

8. **Testing Setup** (30 min)
   - pytest configurado
   - 10+ tests corriendo

---

## 🎓 Conocimientos Necesarios

### Tecnologías Nuevas
- **SQLCipher**: Encriptación transparente de SQLite
- **Argon2id**: Algoritmo KDF moderno (mejor que bcrypt)
- **Keyring**: Acceso a keychain del OS
- **slowapi**: Rate limiting para FastAPI

### Conceptos de Seguridad
- Key Derivation Functions (KDF)
- Password hashing vs encryption
- Rate limiting strategies
- JWT token management

---

## 🔗 Referencias Útiles

### Documentación Interna
- [DATABASE.md](DATABASE.md) - Líneas 48-267 (modelos a crear)
- [SECURITY.md](SECURITY.md) - Líneas 153-337 (SQLCipher + Argon2id)
- [ROADMAP.md](ROADMAP.md) - Líneas 25-130 (Sprint 0 detallado)

### Documentación Externa
- [SQLCipher Docs](https://www.zetetic.net/sqlcipher/documentation/)
- [Passlib Argon2](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html)
- [FastAPI JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [pytest Fixtures](https://docs.pytest.org/en/latest/fixture.html)

---

## 🚨 Bloqueadores Potenciales

### Bloqueador #1: SQLCipher no compila
**Síntoma**: Error al instalar pysqlcipher3  
**Solución**: Usar sqlcipher3-binary o Docker  
**Tiempo perdido estimado**: 30-60 min

### Bloqueador #2: Argon2 muy lento en tests
**Síntoma**: Tests tardan >2 segundos cada uno  
**Solución**: Reducir memory_cost en tests (2048 en lugar de 65536)  
**Workaround**: Mock password hashing en tests

### Bloqueador #3: Keyring no funciona en headless
**Síntoma**: Error al acceder keychain del OS  
**Solución**: Usar keyrings.alt (backend alternativo)  
**Workaround**: Fallback a archivo .env

---

## 📊 Métricas de Éxito

Al finalizar la próxima sesión, deberías tener:

| Métrica | Objetivo |
|---------|----------|
| Modelos creados | 7/19 (37%) |
| Tests passing | 25+ |
| Coverage | 70%+ |
| Tablas en DB | 7/19 |
| Endpoints funcionando | 4 (auth) |
| Tiempo invertido | 5-8 horas |
| Progreso Sprint 0 | 100% ✅ |

---

## 💡 Tips para Éxito

1. **Empezar con SQLCipher**: Es crítico, bloquea todo lo demás
2. **Tests desde el inicio**: No dejar para el final
3. **Commits pequeños**: Cada modelo = 1 commit
4. **Seguir DATABASE.md**: No inventar schema
5. **Usar copilot agresivamente**: Para boilerplate SQLAlchemy
6. **Validar en cada paso**: No avanzar si algo falla

---

**Preparado por**: GitHub Copilot  
**Fecha**: 17 febrero 2026  
**Próxima revisión**: 24 febrero 2026
