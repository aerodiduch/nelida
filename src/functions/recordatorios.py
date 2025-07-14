"""
Funciones de recordatorios para function calling con OpenAI
"""
from datetime import datetime, timedelta
import re
from typing import Dict, Any, List
from loguru import logger

from ..database.models import recordatorio_model
from ..utils.bot_logger import bot_logger

def parse_fecha_inteligente(texto_fecha: str) -> datetime:
    """
    Parser inteligente de fechas en español
    
    Args:
        texto_fecha: Texto describiendo la fecha (ej: "mañana", "viernes", "próxima semana")
    """
    now = datetime.now()
    texto_lower = texto_fecha.lower().strip()
    
    # Casos específicos
    if "mañana" in texto_lower:
        return now + timedelta(days=1)
    elif "hoy" in texto_lower:
        return now + timedelta(hours=2)  # 2 horas desde ahora
    elif "pasado mañana" in texto_lower:
        return now + timedelta(days=2)
    elif "próxima semana" in texto_lower or "semana que viene" in texto_lower:
        return now + timedelta(days=7)
    elif "próximo mes" in texto_lower or "mes que viene" in texto_lower:
        return now + timedelta(days=30)
    
    # Días de la semana
    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    
    for dia_nombre, dia_num in dias_semana.items():
        if dia_nombre in texto_lower:
            dias_hasta = (dia_num - now.weekday()) % 7
            if dias_hasta == 0:  # Si es hoy, asumir próxima semana
                dias_hasta = 7
            return now + timedelta(days=dias_hasta)
    
    # Por defecto, mañana
    return now + timedelta(days=1)

async def crear_recordatorio(contenido: str, fecha_texto: str = "mañana", prioridad: str = "media", user_id: int = None) -> Dict[str, Any]:
    """
    Crear un nuevo recordatorio
    
    Args:
        contenido: Qué recordar
        fecha_texto: Cuándo recordar (en lenguaje natural)
        prioridad: alta, media, baja
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        # Parse de la fecha
        fecha_recordatorio = parse_fecha_inteligente(fecha_texto)
        
        # Crear en la base de datos
        recordatorio_id = recordatorio_model.crear(
            contenido=contenido,
            fecha_recordatorio=fecha_recordatorio,
            user_id=user_id,
            prioridad=prioridad
        )
        
        # Log detallado
        bot_logger.log_function_call(
            user_id, "usuario", "crear_recordatorio_ai",
            success=True, 
            details=f"ID: {recordatorio_id}, Fecha: {fecha_recordatorio}"
        )
        
        return {
            "success": True,
            "recordatorio_id": recordatorio_id,
            "contenido": contenido,
            "fecha": fecha_recordatorio.strftime("%d/%m/%Y %H:%M"),
            "prioridad": prioridad
        }
        
    except Exception as e:
        logger.error(f"Error creando recordatorio: {e}")
        bot_logger.log_function_call(
            user_id, "usuario", "crear_recordatorio_ai",
            success=False, error=str(e)
        )
        return {
            "success": False,
            "error": str(e)
        }

async def listar_recordatorios(solo_pendientes: bool = False, user_id: int = None) -> Dict[str, Any]:
    """
    Listar recordatorios del usuario
    
    Args:
        solo_pendientes: Si mostrar solo los pendientes
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        status_filter = "pendiente" if solo_pendientes else None
        recordatorios = recordatorio_model.listar_por_usuario(user_id, status=status_filter)
        
        # Formatear para la respuesta
        recordatorios_formateados = []
        for rec in recordatorios:
            recordatorios_formateados.append({
                "id": rec['id'],
                "contenido": rec['contenido'],
                "fecha": rec['fecha_recordatorio'],
                "prioridad": rec['prioridad'],
                "status": rec['status']
            })
        
        tipo = "pendientes" if solo_pendientes else "todos"
        bot_logger.log_function_call(
            user_id, "usuario", f"listar_recordatorios_{tipo}",
            success=True, 
            details=f"{len(recordatorios)} encontrados"
        )
        
        return {
            "success": True,
            "recordatorios": recordatorios_formateados,
            "total": len(recordatorios),
            "tipo": tipo
        }
        
    except Exception as e:
        logger.error(f"Error listando recordatorios: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def completar_recordatorio(recordatorio_id: int, user_id: int = None) -> Dict[str, Any]:
    """
    Marcar un recordatorio como completado
    
    Args:
        recordatorio_id: ID del recordatorio
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        # Verificar que el recordatorio existe y es del usuario
        recordatorio = recordatorio_model.obtener_por_id(recordatorio_id)
        if not recordatorio or recordatorio['user_id'] != user_id:
            return {
                "success": False,
                "error": f"Recordatorio {recordatorio_id} no encontrado o no te pertenece"
            }
        
        # Actualizar status
        success = recordatorio_model.actualizar_status(recordatorio_id, "completado")
        
        if success:
            bot_logger.log_function_call(
                user_id, "usuario", "completar_recordatorio_ai",
                success=True, details=f"ID: {recordatorio_id}"
            )
            
            return {
                "success": True,
                "recordatorio_id": recordatorio_id,
                "contenido": recordatorio['contenido'],
                "status": "completado"
            }
        else:
            return {
                "success": False,
                "error": "No se pudo actualizar el recordatorio"
            }
        
    except Exception as e:
        logger.error(f"Error completando recordatorio: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Definiciones de funciones para OpenAI Function Calling
RECORDATORIO_FUNCTIONS = {
    "crear_recordatorio": {
        "type": "function",
        "function": {
            "name": "crear_recordatorio",
            "description": "Crear un nuevo recordatorio para el usuario. Usar cuando el usuario dice algo como 'recuérdame', 'anota que tengo que', 'no me olvides de', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenido": {
                        "type": "string",
                        "description": "Qué tiene que recordar (ej: 'llamar al médico', 'comprar leche')"
                    },
                    "fecha_texto": {
                        "type": "string", 
                        "description": "Cuándo recordar en lenguaje natural (ej: 'mañana', 'viernes', 'próxima semana', 'hoy')",
                        "default": "mañana"
                    },
                    "prioridad": {
                        "type": "string",
                        "enum": ["alta", "media", "baja"],
                        "description": "Prioridad del recordatorio",
                        "default": "media"
                    }
                },
                "required": ["contenido"]
            }
        }
    },
    
    "listar_recordatorios": {
        "type": "function", 
        "function": {
            "name": "listar_recordatorios",
            "description": "Mostrar los recordatorios del usuario. Usar cuando pregunten '¿qué recordatorios tengo?', 'mostrame mis pendientes', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "solo_pendientes": {
                        "type": "boolean",
                        "description": "Si mostrar solo los recordatorios pendientes o todos",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    
    "completar_recordatorio": {
        "type": "function",
        "function": {
            "name": "completar_recordatorio", 
            "description": "Marcar un recordatorio como completado. Usar cuando digan 'ya hice X', 'completé el recordatorio Y', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recordatorio_id": {
                        "type": "integer",
                        "description": "ID del recordatorio a completar"
                    }
                },
                "required": ["recordatorio_id"]
            }
        }
    }
}