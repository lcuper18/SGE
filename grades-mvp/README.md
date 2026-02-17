# SGE Grades MVP - Desarrollo

> Módulo independiente de calificaciones offline para docentes

## 📚 Documentación Completa

Ver [/docs/mvp-grades](../docs/mvp-grades/) para documentación detallada:
- [README.md](../docs/mvp-grades/README.md) - Overview general
- [ARCHITECTURE.md](../docs/mvp-grades/ARCHITECTURE.md) - Arquitectura técnica
- [DATABASE.md](../docs/mvp-grades/DATABASE.md) - Esquema SQLite
- [ROADMAP.md](../docs/mvp-grades/ROADMAP.md) - Plan de 15 semanas
- [SECURITY.md](../docs/mvp-grades/SECURITY.md) - Implementación de seguridad

## 🚀 Quick Start

### Requisitos
- Node.js 18+
- Python 3.11+
- Git

### Instalación

```bash
# 1. Instalar dependencias raíz (Electron)
npm install

# 2. Instalar frontend
cd frontend
npm install
cd ..

# 3. Crear entorno virtual Python
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Desarrollo

```bash
# Terminal único (recomendado)
npm start

# O manualmente en 3 terminales:
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Electron
npm run electron:dev
```

Aplicación abrirá en `http://localhost:3000` dentro de Electron.

## 🧪 Testing

```bash
# Backend (pytest)
cd backend && pytest

# Frontend (Jest)
cd frontend && npm test

# E2E (Playwright)
npm run test:e2e
```

## 📦 Build

```bash
# Build completo
npm run build

# Instaladores en dist/
# - Windows: SGE-Calificaciones-Setup.exe
# - macOS: SGE-Calificaciones.dmg
# - Linux: SGE-Calificaciones.AppImage
```

## 🔐 Seguridad

**CRÍTICO**: Este proyecto maneja datos de menores. Seguridad implementada desde Sprint 0:
- ✅ SQLCipher AES-256
- ✅ Argon2id para passwords
- ✅ Rate limiting
- ✅ Electron hardened
- ✅ Input sanitization
- ✅ Audit logs

Ver [SECURITY.md](../docs/mvp-grades/SECURITY.md) para detalles.

## 📁 Estructura

```
grades-mvp/
├── electron/          # Proceso principal Electron
│   ├── main.js       # Entry point
│   └── preload.js    # IPC bridge seguro
├── frontend/         # React + TypeScript
│   └── src/
├── backend/          # FastAPI + SQLCipher
│   ├── app/
│   └── tests/
├── package.json      # Root config
└── README.md         # Este archivo
```

## 🐛 Troubleshooting

### Backend no inicia
```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Frontend no compila
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Electron no abre
```bash
rm -rf node_modules package-lock.json
npm install
```

## 📞 Contacto

- Issues: Etiquetar con `mvp-grades`
- Rama: `feature/mvp-grades`
- Documentación: `/docs/mvp-grades/`

---

**Inicio desarrollo**: 17 feb 2026  
**Entrega MVP**: 2 jun 2026 (15 semanas)
