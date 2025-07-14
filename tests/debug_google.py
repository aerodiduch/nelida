#!/usr/bin/env python3
"""
Script para debuggear la configuración de Google Search API
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 Debug Google Search API Configuration")
print("=" * 50)

# 1. Verificar variables de entorno
api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
cx = os.getenv('GOOGLE_SEARCH_CX')

print(f"📋 Variables de entorno:")
print(f"   GOOGLE_SEARCH_API_KEY: {'✅ Presente' if api_key else '❌ Ausente'}")
if api_key:
    print(f"   Valor: {api_key[:15]}...{api_key[-5:] if len(api_key) > 20 else api_key}")
    
print(f"   GOOGLE_SEARCH_CX: {'✅ Presente' if cx else '❌ Ausente'}")
if cx:
    print(f"   Valor: {cx}")

print()

# 2. Intentar importar y crear cliente
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from src.functions.busquedas import GoogleSearchClient
    
    print("📦 Importación exitosa de GoogleSearchClient")
    
    # Crear cliente
    client = GoogleSearchClient()
    print(f"🔧 Cliente creado: {'✅ Disponible' if client.is_available() else '❌ No disponible'}")
    
    # Verificar atributos del cliente
    print(f"   api_key: {'✅ Presente' if client.api_key else '❌ Ausente'}")
    print(f"   search_engine_id: {'✅ Presente' if client.search_engine_id else '❌ Ausente'}")
    print(f"   service: {'✅ Creado' if client.service else '❌ No creado'}")
    
    if client.api_key:
        print(f"   API Key: {client.api_key[:15]}...{client.api_key[-5:]}")
    if client.search_engine_id:
        print(f"   CX: {client.search_engine_id}")
        
    # 3. Intentar búsqueda de prueba si está disponible
    if client.is_available():
        print("\n🔍 Probando búsqueda...")
        try:
            results = client.search("test", 1)
            print(f"✅ Búsqueda exitosa: {len(results)} resultados")
            if results:
                print(f"   Primer resultado: {results[0]['title']}")
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
    else:
        print("\n⚠️ Cliente no disponible - no se puede probar búsqueda")
    
except Exception as e:
    print(f"❌ Error importando: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Debug completado")