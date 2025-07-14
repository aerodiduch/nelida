#!/usr/bin/env python3
"""
Script para probar la base de datos de recordatorios
"""
import sys
import os
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import database, recordatorio_model
from loguru import logger

def test_database():
    """Probar operaciones básicas de la base de datos"""
    
    print("🧪 Probando base de datos de recordatorios...")
    
    # Usuario de prueba
    user_id = 12345
    
    try:
        # 1. Crear algunos recordatorios de prueba
        print("\n1️⃣ Creando recordatorios de prueba...")
        
        # Recordatorio para mañana
        fecha_manana = datetime.now() + timedelta(days=1)
        id1 = recordatorio_model.crear(
            contenido="Llamar al médico",
            fecha_recordatorio=fecha_manana,
            user_id=user_id,
            prioridad="alta"
        )
        print(f"✅ Recordatorio creado con ID: {id1}")
        
        # Recordatorio para la próxima semana
        fecha_semana = datetime.now() + timedelta(days=7)
        id2 = recordatorio_model.crear(
            contenido="Renovar seguro del auto",
            fecha_recordatorio=fecha_semana,
            user_id=user_id,
            prioridad="media"
        )
        print(f"✅ Recordatorio creado con ID: {id2}")
        
        # Recordatorio urgente
        fecha_hoy = datetime.now() + timedelta(hours=2)
        id3 = recordatorio_model.crear(
            contenido="Revisar correos",
            fecha_recordatorio=fecha_hoy,
            user_id=user_id,
            prioridad="baja"
        )
        print(f"✅ Recordatorio creado con ID: {id3}")
        
        # 2. Listar todos los recordatorios del usuario
        print("\n2️⃣ Listando recordatorios...")
        recordatorios = recordatorio_model.listar_por_usuario(user_id)
        print(f"📋 Encontrados {len(recordatorios)} recordatorios:")
        
        for rec in recordatorios:
            print(f"  • ID {rec['id']}: {rec['contenido']} "
                  f"({rec['prioridad']}, {rec['status']}) - {rec['fecha_recordatorio']}")
        
        # 3. Obtener un recordatorio específico
        print("\n3️⃣ Obteniendo recordatorio específico...")
        rec_especifico = recordatorio_model.obtener_por_id(id1)
        if rec_especifico:
            print(f"🔍 Recordatorio {id1}: {rec_especifico['contenido']}")
        
        # 4. Marcar uno como completado
        print("\n4️⃣ Marcando recordatorio como completado...")
        success = recordatorio_model.actualizar_status(id1, "completado")
        print(f"✅ Status actualizado: {success}")
        
        # 5. Listar solo pendientes
        print("\n5️⃣ Listando solo pendientes...")
        pendientes = recordatorio_model.listar_por_usuario(user_id, status="pendiente")
        print(f"⏳ Recordatorios pendientes: {len(pendientes)}")
        
        for rec in pendientes:
            print(f"  • {rec['contenido']} - {rec['fecha_recordatorio']}")
        
        # 6. Probar recordatorios que deben notificarse
        print("\n6️⃣ Recordatorios que deben notificarse ahora...")
        fecha_limite = datetime.now() + timedelta(hours=3)
        por_notificar = recordatorio_model.obtener_pendientes_hasta(fecha_limite)
        print(f"🔔 Para notificar: {len(por_notificar)}")
        
        for rec in por_notificar:
            print(f"  • {rec['contenido']} - {rec['fecha_recordatorio']}")
        
        print("\n✅ ¡Todas las pruebas pasaron correctamente!")
        print("🗃️ Base de datos creada en: data/nelida.db")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        logger.error(f"Error probando BD: {e}")

if __name__ == "__main__":
    test_database()