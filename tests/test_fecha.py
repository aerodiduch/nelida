#!/usr/bin/env python3
"""
Test para probar la nueva función de fecha/tiempo
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.functions.fecha_tiempo import obtener_fecha_actual

async def test_fecha():
    """Probar función de fecha"""
    
    print("📅 Probando función de fecha/tiempo...")
    print("=" * 50)
    
    try:
        resultado = obtener_fecha_actual(user_id=12345)
        
        if resultado['success']:
            print("✅ Función exitosa")
            print(f"📅 Fecha actual: {resultado['fecha_actual']}")
            print(f"🕐 Hora actual: {resultado['hora_actual']}")
            print(f"📅 Fecha mañana: {resultado['fecha_mañana']}")
            print(f"🌍 Timezone: {resultado['timezone']}")
            
            print("\n🎯 Esto ayudará a Nélida a:")
            print("• Validar que 'mañana' sea realmente mañana")
            print("• Dar fechas específicas en respuestas de clima")
            print("• Ser más precisa con recordatorios")
            
        else:
            print(f"❌ Error: {resultado['error']}")
            
    except Exception as e:
        print(f"💥 Error en test: {e}")
    
    print("=" * 50)
    print("🏁 Test completado")

if __name__ == "__main__":
    asyncio.run(test_fecha())