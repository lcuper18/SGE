#!/usr/bin/env python3
"""
Script para verificar tablas en la base de datos SQLCipher
"""
from pysqlcipher3 import dbapi2 as sqlite
from app.database import ENCRYPTION_KEY, DB_PATH

# Conectar a la base de datos
conn = sqlite.connect(DB_PATH)
cursor = conn.cursor()

# Establecer clave
cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}'")

# Obtener lista de tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 60)
print("TABLAS EN LA BASE DE DATOS ENCRIPTADA")
print("=" * 60)
print(f"\n📊 Total de tablas: {len(tables)}\n")

for i, (table_name,) in enumerate(tables, 1):
    print(f"{i}. {table_name}")
    
    # Obtener columnas de cada tabla
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"   └─ Columnas: {len(columns)}")
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        is_pk = " [PK]" if col[5] else ""
        is_notnull = " [NOT NULL]" if col[3] else ""
        print(f"      • {col_name}: {col_type}{is_pk}{is_notnull}")
    print()

conn.close()

print("=" * 60)
print("✅ Verificación completa")
print("=" * 60)
