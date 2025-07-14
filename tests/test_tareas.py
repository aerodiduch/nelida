#!/usr/bin/env python3
"""
Test del sistema de tareas de Nelida
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from src.database.models import tarea_model
from src.functions.tareas import crear_tarea, crear_tareas_multiples, listar_tareas, completar_tareas_multiples, buscar_tareas

async def test_sistema_tareas():
    """Test completo del sistema de tareas"""
    print("🧪 Iniciando test del sistema de tareas...")
    
    # Usuario de prueba
    test_user_id = 999999
    
    try:
        # 1. Test de creación múltiple desde una frase
        print("\n1️⃣ Probando creación múltiple desde una frase...")
        texto_multiples = "tengo que llamar al médico, comprar leche y pan, estudiar para el examen, limpiar la casa"
        
        resultado = await crear_tareas_multiples(texto_multiples, test_user_id)
        if resultado['success']:
            print(f"✅ Tareas múltiples creadas: {resultado['total_creadas']}")
            for tarea in resultado['tareas_creadas']:
                print(f"   - {tarea['contenido']} [{tarea['prioridad']} - {tarea['categoria']}]")
        else:
            print(f"❌ Error creando tareas múltiples: {resultado['message']}")
        
        # 2. Crear una tarea individual adicional
        print("\n2️⃣ Creando tarea individual adicional...")
        resultado = await crear_tarea("resolver problema X del trabajo", test_user_id)
        if resultado['success']:
            print(f"✅ Tarea individual creada: {resultado['contenido']}")
        else:
            print(f"❌ Error: {resultado['message']}")
        
        # 3. Listar tareas pendientes
        print("\n3️⃣ Listando tareas pendientes...")
        resultado = await listar_tareas(test_user_id, status="pendiente")
        
        if resultado['success']:
            print(f"📋 Tareas pendientes encontradas: {resultado['total']}")
            for tarea in resultado['tareas']:
                print(f"   - ID {tarea['id']}: {tarea['contenido']} [{tarea['prioridad']} - {tarea['categoria']}]")
        else:
            print(f"❌ Error listando tareas: {resultado['message']}")
        
        # 4. Test de completado múltiple
        print("\n4️⃣ Probando completado múltiple...")
        texto_completado = "ya llamé al médico y también compré leche"
        
        resultado = await completar_tareas_multiples(texto_completado, test_user_id)
        
        if resultado['success']:
            print(f"✅ Tareas completadas: {resultado['total_completadas']}")
            print(f"🔍 Palabras clave detectadas: {resultado['palabras_clave']}")
            
            for tarea in resultado['completadas']:
                print(f"   - Completada: {tarea['contenido']}")
            
            if resultado['no_encontradas']:
                print(f"⚠️ No encontradas: {resultado['no_encontradas']}")
        else:
            print(f"❌ Error en completado múltiple: {resultado['message']}")
        
        # 5. Verificar que se completaron
        print("\n5️⃣ Verificando tareas completadas...")
        resultado = await listar_tareas(test_user_id, status="completado")
        
        if resultado['success']:
            print(f"✅ Tareas completadas: {resultado['total']}")
            for tarea in resultado['tareas']:
                print(f"   - ID {tarea['id']}: {tarea['contenido']}")
        
        # 6. Test de búsqueda
        print("\n6️⃣ Probando búsqueda de tareas...")
        resultado = await buscar_tareas("examen", test_user_id)
        
        if resultado['success']:
            print(f"🔍 Tareas encontradas con 'examen': {resultado['total']}")
            for tarea in resultado['tareas']:
                print(f"   - {tarea['contenido']} [{tarea['status']}]")
        
        # 7. Listar todas las tareas
        print("\n7️⃣ Resumen final - todas las tareas...")
        resultado = await listar_tareas(test_user_id, status="todas")
        
        if resultado['success']:
            print(f"📊 Total de tareas: {resultado['total']}")
            pendientes = len([t for t in resultado['tareas'] if t['status'] == 'pendiente'])
            completadas = len([t for t in resultado['tareas'] if t['status'] == 'completado'])
            print(f"   - Pendientes: {pendientes}")
            print(f"   - Completadas: {completadas}")
        
        print("\n✅ Test completado exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar datos de prueba
        print("\n🧹 Limpiando datos de prueba...")
        try:
            # Eliminar todas las tareas del usuario de prueba
            from src.database.models import database
            with database.get_connection() as conn:
                cursor = conn.execute("DELETE FROM tareas WHERE user_id = ?", (test_user_id,))
                eliminadas = cursor.rowcount
                conn.commit()
                print(f"🗑️ {eliminadas} tareas de prueba eliminadas")
        except Exception as e:
            print(f"⚠️ Error limpiando datos: {e}")

if __name__ == "__main__":
    asyncio.run(test_sistema_tareas())