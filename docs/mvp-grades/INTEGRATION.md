# Guía de Integración con SGE Principal

## 🎯 Objetivo de Integración

Permitir que datos capturados offline en el MVP de Calificaciones se sincronicen con el sistema SGE principal (Django + PostgreSQL) cuando haya conectividad, manteniendo coherencia y resolviendo conflictos de manera predecible.

## 📊 Estado Actual

### MVP Módulo de Calificaciones (Este proyecto)
- **Base de datos**: SQLite local
- **Backend**: FastAPI
- **Modo**: Completamente offline
- **Datos**: Asistencia + Calificaciones + Evaluaciones detalladas

### SGE Principal (Proyecto main)
- **Base de datos**: PostgreSQL multi-tenant
- **Backend**: Django REST Framework
- **Modo**: Requiere internet
- **Phase 1 (MVP)**: Solo asistencia + estructura académica
- **Phase 2**: Grades & Transcripts (pendiente)

## 🔄 Estrategia de Integración

### Enfoque: Sincronización Unidireccional Inicial

**Fase 1** (Corto plazo): MVP → SGE (solo upload)
- Docente trabaja offline en MVP
- Al tener internet: sube datos a SGE
- SGE es fuente de verdad final
- Conflictos se resuelven con política "server wins"

**Fase 2** (Mediano plazo): Bidireccional con merge inteligente
- Descargar estudiantes/grupos desde SGE
- Subir calificaciones a SGE
- Detección y resolución de conflictos

**Fase 3** (Largo plazo): Real-time sync opcional
- WebSocket para notificaciones
- Caché sincronizado automáticamente
- Trabajo colaborativo (múltiples docentes)

---

## 🏗️ Arquitectura de Sincronización

### Componentes Necesarios

```
┌─────────────────┐                    ┌──────────────────┐
│  MVP Grades     │                    │   SGE Principal  │
│  (Electron)     │                    │   (Django)       │
├─────────────────┤                    ├──────────────────┤
│                 │                    │                  │
│  SQLite Local   │  ═══ HTTPS ═══>   │  PostgreSQL      │
│                 │    (API REST)      │                  │
│  sync_queue ─┐  │                    │  /api/v1/sync/   │
│               │  │                    │                  │
│  SyncService ─┘  │                    │  SyncView        │
│                 │                    │  ConflictResolver│
│  Auth (JWT) ────┼──── Token ───────> │  Auth Middleware │
│                 │                    │                  │
└─────────────────┘                    └──────────────────┘
```

### Flujo de Sincronización

```
1. MVP: Usuario hace login con credenciales SGE
   ↓
2. MVP: Obtiene JWT token desde SGE /api/v1/auth/login/
   ↓
3. MVP: Prepara batch de datos (attendance, grades)
   ↓
4. MVP: POST /api/v1/sync/upload/ con token JWT
   ↓
5. SGE: Valida token y permisos
   ↓
6. SGE: Por cada registro:
   - Verifica existencia (student_id, date, etc.)
   - Compara timestamps si existe
   - Aplica regla de conflicto
   - Guarda en PostgreSQL
   ↓
7. SGE: Retorna resultado {accepted: [], conflicts: [], errors: []}
   ↓
8. MVP: Actualiza sync_queue con estados
   ↓
9. MVP: Marca registros como 'synced' o 'conflict'
```

---

## 🔌 API Endpoints Requeridos en SGE

### 1. Autenticación extendida

#### `POST /api/v1/auth/login_external/`
Login para clientes offline (MVP)

**Request:**
```json
{
  "email": "teacher@school.edu.cr",
  "password": "***",
  "client_type": "mvp_grades",
  "client_version": "1.0.0"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": 42,
    "email": "teacher@school.edu.cr",
    "role": "teacher",
    "school_id": 15
  },
  "sync_capabilities": {
    "can_upload_attendance": true,
    "can_upload_grades": true,
    "can_download_students": true
  }
}
```

### 2. Descargar datos iniciales

#### `GET /api/v1/sync/initial_data/`
Descarga estructura académica + estudiantes para setup offline

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query params:**
```
?academic_year_id=5
```

**Response:**
```json
{
  "academic_year": {
    "id": 5,
    "name": "Año Lectivo 2026",
    "start_date": "2026-02-01",
    "end_date": "2027-01-31"
  },
  "periods": [
    {
      "id": 10,
      "name": "Primer Semestre",
      "start_date": "2026-02-01",
      "end_date": "2026-07-15"
    }
  ],
  "grades": [...],
  "groups": [...],
  "subgroups": [...],
  "subjects": [...],
  "teacher_assignments": [
    {
      "id": 123,
      "teacher_id": 42,
      "subject_id": 8,
      "group_id": 15,
      "subgroup_id": null
    }
  ],
  "students": [
    {
      "id": 501,
      "student_id": "2026-7-1-001",
      "first_name": "Ana",
      "last_name": "López",
      "group_id": 15,
      "subgroup_id": null,
      "status": "active"
    }
  ],
  "time_slots": [...],
  "last_sync": "2026-02-16T10:30:00Z"
}
```

### 3. Subir asistencia

#### `POST /api/v1/sync/attendance/`
Upload batch de registros de asistencia

**Request:**
```json
{
  "records": [
    {
      "student_id": "2026-7-1-001",
      "subject_id": 8,
      "date": "2026-02-15",
      "time_slot_id": 3,
      "status": "present",
      "created_at": "2026-02-15T08:05:00Z",
      "updated_at": "2026-02-15T08:05:00Z",
      "mvp_id": 1234  // ID local del MVP
    },
    {
      "student_id": "2026-7-1-002",
      "subject_id": 8,
      "date": "2026-02-15",
      "time_slot_id": 3,
      "status": "absent_unexcused",
      "created_at": "2026-02-15T08:06:00Z",
      "updated_at": "2026-02-15T08:06:00Z",
      "mvp_id": 1235
    }
  ],
  "metadata": {
    "total_records": 2,
    "date_range": ["2026-02-15", "2026-02-15"],
    "mvp_version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "summary": {
    "total_received": 2,
    "accepted": 2,
    "conflicts": 0,
    "errors": 0
  },
  "accepted": [
    {
      "mvp_id": 1234,
      "sge_id": 9876,
      "student_id": "2026-7-1-001",
      "status": "created"
    },
    {
      "mvp_id": 1235,
      "sge_id": 9877,
      "student_id": "2026-7-1-002",
      "status": "created"
    }
  ],
  "conflicts": [],
  "errors": [],
  "sync_timestamp": "2026-02-16T10:35:00Z"
}
```

**Conflicto example:**
```json
{
  "conflicts": [
    {
      "mvp_id": 1234,
      "student_id": "2026-7-1-001",
      "field": "status",
      "mvp_value": "present",
      "sge_value": "absent_unexcused",
      "mvp_timestamp": "2026-02-15T08:05:00Z",
      "sge_timestamp": "2026-02-15T07:50:00Z",
      "resolution": "server_wins",
      "message": "SGE tiene timestamp más antiguo, se mantiene valor del servidor"
    }
  ]
}
```

### 4. Subir calificaciones

#### `POST /api/v1/sync/grades/`
Upload de evaluaciones y notas

**Request:**
```json
{
  "assignments": [
    {
      "mvp_id": 50,
      "name": "Proyecto Revolución Francesa",
      "subject_id": 8,
      "group_id": 15,
      "period_id": 10,
      "rubric_component": "proyecto",
      "max_points": 30,
      "due_date": "2026-03-15",
      "criteria": [
        {"name": "Investigación", "max_points": 10},
        {"name": "Presentación", "max_points": 10},
        {"name": "Creatividad", "max_points": 10}
      ]
    }
  ],
  "scores": [
    {
      "assignment_mvp_id": 50,
      "student_id": "2026-7-1-001",
      "criteria_scores": [
        {"criteria_name": "Investigación", "points": 8.5},
        {"criteria_name": "Presentación", "points": 9.0},
        {"criteria_name": "Creatividad", "points": 7.5}
      ],
      "total_points": 25.0,
      "graded_at": "2026-03-20T14:30:00Z"
    }
  ],
  "metadata": {
    "teacher_id": 42,
    "sync_date": "2026-03-21T10:00:00Z"
  }
}
```

**Response:**
```json
{
  "summary": {
    "assignments_created": 1,
    "scores_accepted": 1,
    "conflicts": 0,
    "errors": 0
  },
  "assignments": [
    {
      "mvp_id": 50,
      "sge_id": 201,
      "status": "created"
    }
  ],
  "scores": [
    {
      "assignment_mvp_id": 50,
      "student_id": "2026-7-1-001",
      "status": "accepted"
    }
  ]
}
```

### 5. Verificar estado de sincronización

#### `GET /api/v1/sync/status/`
Consultar última sincronización y detectar cambios en el servidor

**Response:**
```json
{
  "last_sync_from_client": "2026-03-21T10:00:00Z",
  "server_has_updates": true,
  "updates_summary": {
    "new_students": 5,
    "updated_students": 2,
    "new_assignments": 0
  },
  "pending_downloads": true
}
```

---

## 🔐 Autenticación y Seguridad

### Token Management en MVP

```python
# backend/app/services/sge_auth_service.py
import requests
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import APICredentials

class SGEAuthService:
    def __init__(self):
        self.base_url = "https://sge.school.edu.cr"  # URL del SGE
        
    def login(self, email: str, password: str):
        """Login contra SGE y guardar tokens"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login_external/",
            json={
                "email": email,
                "password": password,
                "client_type": "mvp_grades",
                "client_version": "1.0.0"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception("Login failed")
        
        data = response.json()
        
        # Guardar tokens en tabla local
        db = SessionLocal()
        cred = APICredentials(
            user_id=self.get_current_user_id(),
            api_url=self.base_url,
            access_token=self._encrypt(data['access_token']),
            refresh_token=self._encrypt(data['refresh_token']),
            expires_at=datetime.utcnow() + timedelta(hours=8),
            last_sync=datetime.utcnow()
        )
        db.add(cred)
        db.commit()
        
        return data
    
    def get_valid_token(self):
        """Obtener token válido (refresh si expiró)"""
        db = SessionLocal()
        cred = db.query(APICredentials).filter_by(
            user_id=self.get_current_user_id()
        ).first()
        
        if not cred:
            raise Exception("No credentials found. Please login.")
        
        # Si el token expiró, hacer refresh
        if cred.expires_at < datetime.utcnow():
            return self._refresh_token(cred)
        
        return self._decrypt(cred.access_token)
    
    def _refresh_token(self, cred):
        """Renovar access token"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/refresh/",
            json={"refresh_token": self._decrypt(cred.refresh_token)},
            timeout=10
        )
        
        data = response.json()
        
        # Actualizar en DB
        cred.access_token = self._encrypt(data['access_token'])
        cred.expires_at = datetime.utcnow() + timedelta(hours=8)
        
        db = SessionLocal()
        db.add(cred)
        db.commit()
        
        return data['access_token']
```

### Encriptación de tokens

```python
from cryptography.fernet import Fernet
import os

class TokenEncryption:
    def __init__(self):
        # Generar key en primera ejecución, guardar en DB o archivo
        key_file = "encryption.key"
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()
        
        self.cipher = Fernet(key)
    
    def encrypt(self, text: str) -> str:
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

---

## 🔄 Lógica de Sincronización

### Servicio de Sync en MVP

```python
# backend/app/services/sync_service.py
import requests
from typing import List, Dict
from app.models import Attendance, SyncQueue
from app.services.sge_auth_service import SGEAuthService
from app.database import SessionLocal

class SyncService:
    def __init__(self):
        self.auth = SGEAuthService()
        self.base_url = "https://sge.school.edu.cr"
    
    def sync_attendance(self, start_date=None, end_date=None):
        """Sincronizar asistencia pendiente"""
        db = SessionLocal()
        
        # Obtener registros pendientes de sync_queue
        pending = db.query(SyncQueue).filter(
            SyncQueue.entity_type == 'attendance',
            SyncQueue.status == 'pending'
        ).limit(100).all()  # Batch de 100
        
        if not pending:
            return {"message": "No pending records"}
        
        # Preparar payload
        records = []
        for item in pending:
            attendance = db.query(Attendance).get(item.entity_id)
            records.append({
                "student_id": attendance.student.student_id,
                "subject_id": attendance.subject_id,
                "date": attendance.date.isoformat(),
                "time_slot_id": attendance.time_slot_id,
                "status": attendance.status,
                "created_at": attendance.created_at.isoformat(),
                "updated_at": attendance.updated_at.isoformat(),
                "mvp_id": attendance.id
            })
        
        # Hacer request a SGE
        token = self.auth.get_valid_token()
        response = requests.post(
            f"{self.base_url}/api/v1/sync/attendance/",
            json={"records": records},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Sync failed: {response.text}")
        
        result = response.json()
        
        # Actualizar sync_queue
        for accepted in result['accepted']:
            item = next(i for i in pending if i.entity_id == accepted['mvp_id'])
            item.status = 'synced'
            item.synced_at = datetime.utcnow()
        
        for conflict in result['conflicts']:
            item = next(i for i in pending if i.entity_id == conflict['mvp_id'])
            item.status = 'conflict'
            item.error_message = conflict['message']
        
        db.commit()
        
        return result
    
    def download_initial_data(self, academic_year_id: int):
        """Descargar estructura académica desde SGE"""
        token = self.auth.get_valid_token()
        
        response = requests.get(
            f"{self.base_url}/api/v1/sync/initial_data/",
            params={"academic_year_id": academic_year_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        
        data = response.json()
        
        # Guardar en SQLite local
        db = SessionLocal()
        
        # Importar students
        for student_data in data['students']:
            student = Student(**student_data)
            db.merge(student)  # Merge para evitar duplicados
        
        # Importar otros datos...
        
        db.commit()
        
        return data
```

### Auto-sync en background (Electron)

```javascript
// electron/services/sync-manager.js
const { ipcMain } = require('electron');

class SyncManager {
  constructor() {
    this.syncInterval = null;
    this.isOnline = false;
  }
  
  startAutoSync() {
    // Detectar conectividad
    this.monitorConnection();
    
    // Intentar sync cada 15 minutos si hay internet
    this.syncInterval = setInterval(() => {
      if (this.isOnline) {
        this.triggerSync();
      }
    }, 15 * 60 * 1000);  // 15 minutos
  }
  
  monitorConnection() {
    require('dns').resolve('www.google.com', (err) => {
      this.isOnline = !err;
    });
    
    setInterval(() => {
      require('dns').resolve('www.google.com', (err) => {
        const wasOnline = this.isOnline;
        this.isOnline = !err;
        
        // Si acaba de conectarse, hacer sync inmediato
        if (!wasOnline && this.isOnline) {
          this.triggerSync();
        }
      });
    }, 60000);  // Check cada minuto
  }
  
  async triggerSync() {
    try {
      // Llamar a backend local que hace requests a SGE
      const response = await fetch('http://localhost:8000/sync/auto', {
        method: 'POST'
      });
      
      const result = await response.json();
      
      // Notificar a renderer process
      this.sendNotification('sync-complete', result);
      
    } catch (error) {
      console.error('Auto-sync failed:', error);
    }
  }
  
  sendNotification(channel, data) {
    const windows = require('electron').BrowserWindow.getAllWindows();
    windows.forEach(win => {
      win.webContents.send(channel, data);
    });
  }
}

module.exports = new SyncManager();
```

---

## ⚖️ Resolución de Conflictos

### Políticas de Conflicto

#### 1. Server Wins (Default)
```python
def resolve_conflict_server_wins(mvp_record, sge_record):
    """
    El servidor siempre tiene razón.
    Registros del MVP se descartan si hay conflicto.
    """
    return {
        "action": "discard_mvp",
        "keep": sge_record,
        "message": "Server record preserved"
    }
```

#### 2. Latest Timestamp Wins
```python
def resolve_conflict_latest_wins(mvp_record, sge_record):
    """
    El registro más reciente (por updated_at) gana.
    """
    if mvp_record.updated_at > sge_record.updated_at:
        return {
            "action": "accept_mvp",
            "keep": mvp_record,
            "message": "MVP record is newer"
        }
    else:
        return {
            "action": "discard_mvp",
            "keep": sge_record,
            "message": "Server record is newer"
        }
```

#### 3. Manual Resolution
```python
def resolve_conflict_manual(mvp_record, sge_record):
    """
    Marcar como conflicto y requerir intervención del usuario.
    """
    return {
        "action": "require_manual",
        "mvp_value": mvp_record.to_dict(),
        "sge_value": sge_record.to_dict(),
        "message": "Manual intervention required"
    }
```

### UI de Resolución de Conflictos

```typescript
// frontend/src/pages/SyncConflicts.tsx
interface Conflict {
  id: number;
  entity_type: string;
  student_name: string;
  field: string;
  mvp_value: any;
  sge_value: any;
  mvp_timestamp: string;
  sge_timestamp: string;
}

function ConflictResolution() {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  
  const resolveConflict = async (conflictId: number, choice: 'mvp' | 'sge') => {
    await api.post(`/sync/conflicts/${conflictId}/resolve`, {
      resolution: choice
    });
    
    // Refrescar lista
    loadConflicts();
  };
  
  return (
    <div>
      <h2>Conflictos de Sincronización</h2>
      {conflicts.map(conflict => (
        <div key={conflict.id} className="conflict-item">
          <h3>{conflict.student_name} - {conflict.field}</h3>
          
          <div className="values">
            <div className="mvp-value">
              <strong>Valor Local (MVP):</strong>
              <code>{JSON.stringify(conflict.mvp_value)}</code>
              <small>{conflict.mvp_timestamp}</small>
              <button onClick={() => resolveConflict(conflict.id, 'mvp')}>
                Usar este
              </button>
            </div>
            
            <div className="sge-value">
              <strong>Valor Servidor (SGE):</strong>
              <code>{JSON.stringify(conflict.sge_value)}</code>
              <small>{conflict.sge_timestamp}</small>
              <button onClick={() => resolveConflict(conflict.id, 'sge')}>
                Usar este
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 📋 Checklist de Implementación

### En SGE Principal (Django)

- [ ] **Endpoints de sync** (Prioridad Alta)
  - [ ] POST /api/v1/auth/login_external/
  - [ ] GET /api/v1/sync/initial_data/
  - [ ] POST /api/v1/sync/attendance/
  - [ ] POST /api/v1/sync/grades/
  - [ ] GET /api/v1/sync/status/

- [ ] **Modelos extendidos** (Phase 2)
  - [ ] Subject model (materias)
  - [ ] Assignment model
  - [ ] EvaluationCriteria model
  - [ ] Grade model con rubrics

- [ ] **Lógica de negocio**
  - [ ] ConflictResolver service
  - [ ] Validación de datos incoming
  - [ ] Logs de auditoría de sincronización

- [ ] **Testing**
  - [ ] Tests de endpoints de sync
  - [ ] Tests de resolución de conflictos
  - [ ] Tests de performance (1000 registros)

### En MVP Módulo de Calificaciones

- [ ] **Auth extendida**
  - [ ] Login contra SGE
  - [ ] Token storage encriptado
  - [ ] Auto-refresh de tokens

- [ ] **Sync service**
  - [ ] SyncService completo
  - [ ] Queue management
  - [ ] Batch uploads
  - [ ] Download inicial

- [ ] **UI de sincronización**
  - [ ] Página Sync con estado
  - [ ] Botón manual "Sincronizar ahora"
  - [ ] Progress indicator
  - [ ] UI de conflictos

- [ ] **Background sync**
  - [ ] Electron sync manager
  - [ ] Detección de conectividad
  - [ ] Auto-sync cada 15 min
  - [ ] Notificaciones desktop

- [ ] **Testing**
  - [ ] Tests de sync service
  - [ ] Tests de manejo de errores
  - [ ] Tests offline → online transition

---

## 🚀 Roadmap de Integración

### Milestone 1: Auth y Download (2 semanas)
- Login contra SGE desde MVP
- Descarga inicial de estudiantes/grupos
- Store tokens encriptados

### Milestone 2: Upload Asistencia (2 semanas)
- Implementar POST /api/v1/sync/attendance/ en SGE
- Batch upload desde MVP
- Manejo básico de errores

### Milestone 3: Resolución de Conflictos (2 semanas)
- Implementar detección de conflictos
- UI para resolución manual
- Políticas configurables

### Milestone 4: Upload Calificaciones (3 semanas)
- Completar Phase 2 en SGE (grades model)
- Implementar POST /api/v1/sync/grades/
- Mapeo de rúbricas MVP → SGE

### Milestone 5: Sync Bidireccional (2 semanas)
- Download updates desde SGE
- Merge inteligente
- Testing completo end-to-end

### Milestone 6: Auto-sync y Polish (1 semana)
- Background sync automático
- Notificaciones
- Logging y monitoreo

**Total estimado: 12 semanas**

---

## 🎯 Criterios de Éxito de Integración

- ✅ Docente puede hacer login con credenciales SGE
- ✅ Download inicial de 500 estudiantes en < 30 segundos
- ✅ Upload de 100 registros de asistencia en < 10 segundos
- ✅ Conflictos detectados correctamente (0 falsos positivos)
- ✅ Sync manual funciona sin internet loss durante proceso
- ✅ Auto-sync detecta reconexión y sincroniza automáticamente
- ✅ UI de conflictos clara y fácil de usar
- ✅ 0 pérdida de datos en sync

---

**Última actualización**: 16 de febrero, 2026  
**Estado**: Diseño completo, implementación pendiente  
**Próximos pasos**: Comenzar con Milestone 1 post-MVP
