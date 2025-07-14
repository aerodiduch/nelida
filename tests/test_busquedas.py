#!/usr/bin/env python3
"""
Script para probar las búsquedas en internet
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar DESPUÉS de cargar las variables de entorno
from src.functions.busquedas import buscar_en_internet, obtener_contenido_pagina, google_client

async def test_busquedas():
    """Probar funciones de búsqueda"""
    
    print("🔍 Probando sistema de búsquedas...")
    print(f"📡 Google API disponible: {'✅ Sí' if google_client.is_available() else '❌ No (usando DuckDuckGo)'}")
    
    try:
        # Test 1: Búsqueda básica
        print("\n1️⃣ Probando búsqueda básica...")
        resultado = await buscar_en_internet("Python programming", num_resultados=3, user_id=12345)
        
        if resultado['success']:
            print(f"✅ Búsqueda exitosa usando: {resultado['metodo']}")
            print(f"📊 Encontrados: {resultado['total']} resultados")
            
            for i, item in enumerate(resultado['resultados'], 1):
                print(f"\n{i}. 📄 {item['title']}")
                print(f"   🔗 {item['link']}")
                print(f"   📝 {item['snippet'][:100]}...")
        else:
            print(f"❌ Error: {resultado['error']}")
        
        # Test 2: Búsqueda en español
        print("\n2️⃣ Probando búsqueda en español...")
        resultado2 = await buscar_en_internet("noticias Argentina", num_resultados=2, user_id=12345)
        
        if resultado2['success']:
            print(f"✅ Búsqueda en español exitosa")
            for i, item in enumerate(resultado2['resultados'], 1):
                print(f"\n{i}. 📄 {item['title']}")
                print(f"   🔗 {item['displayLink']}")
        
        # Test 3: Obtener contenido de página (solo si hay resultados)
        if resultado['success'] and resultado['resultados']:
            print("\n3️⃣ Probando lectura de página...")
            primera_url = resultado['resultados'][0]['link']
            contenido = await obtener_contenido_pagina(primera_url, user_id=12345)
            
            if contenido['success']:
                print(f"✅ Página leída exitosamente")
                print(f"📄 Título: {contenido['title']}")
                print(f"📊 Caracteres: {contenido['length']}")
                print(f"📝 Contenido: {contenido['content'][:200]}...")
            else:
                print(f"❌ Error leyendo página: {contenido['error']}")
        
        print("\n✅ ¡Todas las pruebas completadas!")
        print("🚀 El sistema de búsquedas está listo para usar con Nélida")
        
    except Exception as e:
        print(f"💥 Error en las pruebas: {e}")

if __name__ == "__main__":
    asyncio.run(test_busquedas())