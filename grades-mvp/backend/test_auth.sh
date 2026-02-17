#!/bin/bash
# Test completo de autenticación

echo "=================================================="
echo "   SGE GRADES MVP - Test de Autenticación"
echo "=================================================="
echo ""

# Iniciar backend
echo "1️⃣  Iniciando backend..."
cd /home/lfallas/Workspace/SGE/grades-mvp/backend
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3
echo "✅ Backend iniciado (PID: $BACKEND_PID)"
echo ""

# Test 1: Health check
echo "2️⃣  Test: Health check"
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
echo ""

# Test 2: Registro de usuario
echo "3️⃣  Test: Registro de usuario (profesor2)"
REGISTER_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "profesor2",
    "email": "profesor2@example.com",
    "password": "Password123",
    "full_name": "María López"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

# Test 3: Login
echo "4️⃣  Test: Login"
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"profesor2","password":"Password123"}')
echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extraer token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ No se pudo obtener token"
  kill $BACKEND_PID 2>/dev/null
  exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:50}..."
echo ""

# Test 4: Obtener perfil con token
echo "5️⃣  Test: GET /api/auth/me (con token JWT)"
curl -s http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Test 5: Intento sin token (debe fallar)
echo "6️⃣  Test: GET /api/auth/me (sin token - debe fallar)"
curl -s http://127.0.0.1:8000/api/auth/me | python3 -m json.tool
echo ""

echo "=================================================="
echo "✅ Tests completados"
echo "=================================================="
echo ""

# Detener backend
echo "Deteniendo backend..."
kill $BACKEND_PID 2>/dev/null
sleep 1
echo "✅ Backend detenido"
