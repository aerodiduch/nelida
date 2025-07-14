#!/usr/bin/env python3
"""
Test para verificar que Nélida procese correctamente los resultados de búsqueda
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.simple_ai import SimpleAI

async def test_nelida_noticias():
    """Test directo con Nélida para ver si procesa bien las noticias"""
    
    print("🤖 Test: Nélida procesando noticias")
    print("=" * 50)
    
    # Crear instancia de Nélida
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY no configurado")
        return
    
    ai = SimpleAI(openai_key)
    
    # Registrar función de búsqueda
    from src.functions.busquedas import buscar_en_internet, BUSQUEDA_FUNCTIONS
    ai.register_function("buscar_en_internet", buscar_en_internet, BUSQUEDA_FUNCTIONS["buscar_en_internet"])
    
    # Test query
    query = "noticias mas relevantes de hoy"
    user_id = 12345
    
    print(f"👤 Usuario: '{query}'")
    print("🔄 Procesando con Nélida...")
    print()
    
    try:
        response = await ai.get_response(query, user_id, use_personality=True)
        
        print("🤖 Respuesta de Nélida:")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        print()
        print("🎯 Análisis:")
        if "no tengo acceso" in response.lower() or "te dejo unos" in response.lower():
            print("❌ Nélida sigue dando respuesta genérica")
            print("🔧 Necesita más ajustes en el prompt")
        elif "clarín" in response.lower() or "nación" in response.lower() or "cnn" in response.lower():
            print("✅ ¡Nélida está procesando los resultados!")
            print("🎉 Menciona fuentes específicas")
        else:
            print("🟡 Respuesta ambigua - revisar")
    
    except Exception as e:
        print(f"💥 Error: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_nelida_noticias())