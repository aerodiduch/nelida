#!/usr/bin/env python3
"""
Test para verificar el contexto argentino en búsquedas
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.functions.busquedas import buscar_en_internet

async def test_contexto_argentino():
    """Probar búsquedas generales para ver si incluyen contexto argentino"""
    
    print("🇦🇷 Probando contexto argentino en búsquedas...")
    print("=" * 60)
    
    # Test 1: Búsqueda general de noticias
    print("1️⃣ Búsqueda: 'noticias importantes hoy'")
    print("   (Debería incluir noticias de Argentina)")
    resultado1 = await buscar_en_internet("noticias importantes hoy Argentina", 2, 12345)
    
    if resultado1['success']:
        print(f"✅ {len(resultado1['resultados'])} resultados encontrados")
        for i, res in enumerate(resultado1['resultados'], 1):
            print(f"   {i}. {res['title']}")
            print(f"      Link: {res['displayLink']}")
    else:
        print(f"❌ Error: {resultado1['error']}")
    
    print("\n" + "-" * 60)
    
    # Test 2: Búsqueda de clima
    print("2️⃣ Búsqueda: 'clima mañana'")
    print("   (Debería buscar clima de Buenos Aires)")
    resultado2 = await buscar_en_internet("clima mañana Buenos Aires", 2, 12345)
    
    if resultado2['success']:
        print(f"✅ {len(resultado2['resultados'])} resultados encontrados")
        for i, res in enumerate(resultado2['resultados'], 1):
            print(f"   {i}. {res['title']}")
            print(f"      Link: {res['displayLink']}")
    else:
        print(f"❌ Error: {resultado2['error']}")
    
    print("\n" + "=" * 60)
    print("🎯 Con el nuevo prompt, Nélida debería:")
    print("• Agregar 'Argentina' o 'Buenos Aires' automáticamente")
    print("• Priorizar información local")
    print("• Ser más relevante para usuarios argentinos")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_contexto_argentino())