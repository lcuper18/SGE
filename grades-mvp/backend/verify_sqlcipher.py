#!/usr/bin/env python3
"""
Script de verificación de SQLCipher
Comprueba que pysqlcipher3 esté usando SQLCipher real con encriptación activa
"""
import sys
import os

def verify_sqlcipher():
    """Verifica la instalación de SQLCipher"""
    print("🔍 Verificando SQLCipher...\n")
    
    try:
        from pysqlcipher3 import dbapi2 as sqlite
        print("✅ pysqlcipher3 importado correctamente")
    except ImportError as e:
        print(f"❌ Error al importar pysqlcipher3: {e}")
        return False
    
    # Crear base de datos de prueba en memoria
    try:
        conn = sqlite.connect(':memory:')
        cursor = conn.cursor()
        print("✅ Conexión establecida")
        
        # Activar encriptación
        cursor.execute("PRAGMA key = 'test_password_123'")
        print("✅ PRAGMA key ejecutado")
        
        # Verificar versión de SQLCipher
        cursor.execute("PRAGMA cipher_version")
        version = cursor.fetchone()
        
        if version and version[0]:
            print(f"✅ SQLCipher versión: {version[0]}")
            print("✅ ¡ENCRIPTACIÓN ACTIVA!")
            
            # Crear tabla de prueba
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
            cursor.execute("INSERT INTO test (data) VALUES ('datos_secretos')")
            conn.commit()
            
            # Verificar datos
            cursor.execute("SELECT * FROM test")
            result = cursor.fetchone()
            print(f"✅ Tabla de prueba creada y datos insertados: {result}")
            
            conn.close()
            return True
        else:
            print("❌ No se pudo obtener versión de SQLCipher")
            print("⚠️  Posiblemente usando SQLite estándar (SIN ENCRIPTACIÓN)")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE SQLCIPHER - SGE Grades MVP")
    print("=" * 60 + "\n")
    
    success = verify_sqlcipher()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ RESULTADO: SQLCipher funcionando correctamente")
        print("✅ Base de datos SERÁ ENCRIPTADA")
        sys.exit(0)
    else:
        print("❌ RESULTADO: SQLCipher NO está funcionando")
        print("⚠️  Base de datos NO ESTARÁ ENCRIPTADA")
        sys.exit(1)
    print("=" * 60)
