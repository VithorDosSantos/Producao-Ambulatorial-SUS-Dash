"""
Script de teste para verificar se PORT está sendo lida corretamente
"""
import os
import sys

port = os.getenv("PORT", "8000")
print(f"PORT environment variable: {port}")
print(f"Type: {type(port)}")
print(f"Command would be: uvicorn app.main:app --host 0.0.0.0 --port {port}")
sys.exit(0)
