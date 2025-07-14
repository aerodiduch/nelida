#!/usr/bin/env python3
"""
Debug para simular exactamente la consulta de noticias del usuario
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

async def debug_noticias():
    """Simular la búsqueda de noticias relevantes"""
    
    print("🔍 Debug: 'noticias mas relevantes de hoy'")
    print("=" * 60)
    
    # Simular lo que Nélida debería buscar
    query_esperado = "noticias importantes hoy Argentina Buenos Aires"
    
    print(f"📡 Query que debería usar: '{query_esperado}'")
    print()
    
    try:
        resultado = await buscar_en_internet(query_esperado, 5, 12345)
        
        if resultado['success']:
            print(f"✅ Búsqueda exitosa - {len(resultado['resultados'])} resultados")
            print(f"🔧 Método usado: {resultado['metodo']}")
            print()
            
            print("📰 Resultados encontrados:")
            for i, noticia in enumerate(resultado['resultados'], 1):
                print(f"\n{i}. 📄 {noticia['title']}")
                print(f"   🔗 {noticia['link']}")
                print(f"   📝 {noticia['snippet'][:150]}...")
                print(f"   🌐 Fuente: {noticia['displayLink']}")
            
            print("\n" + "=" * 60)
            print("🎯 Con estos resultados, Nélida DEBERÍA:")
            print("• Resumir las noticias más importantes")
            print("• Mencionar títulos específicos")
            print("• Dar fuentes argentinas")
            print("• NO dar links genéricos")
            
        else:
            print(f"❌ Error en búsqueda: {resultado['error']}")
            print("🔧 Esto explicaría por qué Nélida dio respuesta genérica")
            
    except Exception as e:
        print(f"💥 Excepción: {e}")
        print("🔧 Esto también explicaría la respuesta genérica")
    
    print("\n" + "=" * 60)
    print("🔍 Conclusión:")
    print("Si la búsqueda funciona pero Nélida da respuesta genérica,")
    print("el problema está en el prompt o en el procesamiento de resultados.")

if __name__ == "__main__":
    asyncio.run(debug_noticias())