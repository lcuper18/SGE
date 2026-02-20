"""
Instancia global del rate limiter para SGE Grades MVP.

Módulo independiente para evitar importaciones circulares entre
app/main.py y app/routes/auth.py.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
