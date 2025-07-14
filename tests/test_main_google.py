#!/usr/bin/env python3
"""
Test rápido para verificar que main.py carga Google API correctamente
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar como lo hace main.py
from src.functions.busquedas import buscar_en_internet, obtener_contenido_pagina, BUSQUEDA_FUNCTIONS

# Importar también el cliente para verificar
from src.functions.busquedas import google_client

print("🔍 Test de main.py - Google API")
print("=" * 40)
print(f"📡 Google API disponible: {'✅ Sí' if google_client.is_available() else '❌ No'}")

if google_client.is_available():
    print("✅ ¡Perfecto! main.py va a usar Google API")
else:
    print("⚠️ main.py va a usar DuckDuckGo como fallback")
    
print("=" * 40)