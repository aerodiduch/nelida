"""
Funciones para manejo de notas/anotaciones con lenguaje natural
"""
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from ..database.models import nota_model

async def crear_nota(contenido: str, user_id: int, categoria: str = "general") -> Dict[str, Any]:
    """
    Crear una nueva nota/anotación
    
    Args:
        contenido: Texto de la nota
        user_id: ID del usuario de Telegram
        categoria: Categoría para organizar la nota
    
    Returns:
        Dict con información de la nota creada
    """
    try:
        # Limpiar contenido
        contenido_limpio = contenido.strip()
        
        if not contenido_limpio:
            return {
                "success": False,
                "message": "No puedo crear una nota vacía, pibe"
            }
        
        # Detectar categoría automáticamente si no se especifica
        if categoria == "general":
            categoria_detectada = detectar_categoria_nota(contenido_limpio)
            if categoria_detectada:
                categoria = categoria_detectada
        
        # Crear la nota
        nota_id = nota_model.crear(
            contenido=contenido_limpio,
            user_id=user_id,
            categoria=categoria
        )
        
        return {
            "success": True,
            "nota_id": nota_id,
            "contenido": contenido_limpio,
            "categoria": categoria,
            "message": f"Nota guardada: {contenido_limpio[:50]}{'...' if len(contenido_limpio) > 50 else ''}"
        }
        
    except Exception as e:
        logger.error(f"Error creando nota: {e}")
        return {
            "success": False,
            "message": f"Error al guardar la nota: {str(e)}"
        }

async def listar_notas(user_id: int, categoria: str = None) -> Dict[str, Any]:
    """
    Listar notas del usuario
    
    Args:
        user_id: ID del usuario
        categoria: Filtrar por categoría específica
    
    Returns:
        Dict con lista de notas
    """
    try:
        notas = nota_model.listar_por_usuario(
            user_id=user_id,
            categoria=categoria
        )
        
        return {
            "success": True,
            "notas": notas,
            "total": len(notas),
            "categoria_filtro": categoria
        }
        
    except Exception as e:
        logger.error(f"Error listando notas: {e}")
        return {
            "success": False,
            "message": f"Error al listar notas: {str(e)}"
        }

async def buscar_notas(texto_busqueda: str, user_id: int) -> Dict[str, Any]:
    """
    Buscar notas por contenido
    
    Args:
        texto_busqueda: Texto a buscar en las notas
        user_id: ID del usuario
    
    Returns:
        Dict con notas encontradas
    """
    try:
        notas = nota_model.buscar_por_contenido(texto_busqueda, user_id)
        
        return {
            "success": True,
            "notas": notas,
            "total": len(notas),
            "busqueda": texto_busqueda
        }
        
    except Exception as e:
        logger.error(f"Error buscando notas: {e}")
        return {
            "success": False,
            "message": f"Error al buscar notas: {str(e)}"
        }

async def eliminar_nota(nota_id: int, user_id: int) -> Dict[str, Any]:
    """
    Eliminar una nota específica
    
    Args:
        nota_id: ID de la nota a eliminar
        user_id: ID del usuario
    
    Returns:
        Dict con resultado de la eliminación
    """
    try:
        success = nota_model.eliminar(nota_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": f"Nota {nota_id} eliminada correctamente"
            }
        else:
            return {
                "success": False,
                "message": f"No pude eliminar la nota {nota_id}. Verificá que existe y es tuya."
            }
        
    except Exception as e:
        logger.error(f"Error eliminando nota: {e}")
        return {
            "success": False,
            "message": f"Error al eliminar nota: {str(e)}"
        }

def detectar_categoria_nota(texto: str) -> str:
    """
    Detectar categoría automáticamente basándose en el contenido
    
    Args:
        texto: Texto de la nota
    
    Returns:
        Categoría detectada
    """
    texto_lower = texto.lower()
    
    # Categorías de trabajo
    trabajo_keywords = ["trabajo", "reunión", "proyecto", "cliente", "jefe", "empresa", "oficina", "email"]
    if any(palabra in texto_lower for palabra in trabajo_keywords):
        return "trabajo"
    
    # Categorías de ideas
    ideas_keywords = ["idea", "proyecto personal", "emprendimiento", "negocio", "innovación"]
    if any(palabra in texto_lower for palabra in ideas_keywords):
        return "ideas"
    
    # Categorías personales
    personal_keywords = ["personal", "familia", "amigos", "casa", "comprar"]
    if any(palabra in texto_lower for palabra in personal_keywords):
        return "personal"
    
    # Categorías de estudio
    estudio_keywords = ["curso", "aprender", "estudiar", "libro", "tutorial"]
    if any(palabra in texto_lower for palabra in estudio_keywords):
        return "estudio"
    
    return "general"  # Default

# Definiciones de funciones para OpenAI Function Calling
NOTA_FUNCTIONS = {
    "crear_nota": {
        "type": "function",
        "function": {
            "name": "crear_nota",
            "description": "Guardar una nota o anotación cuando el usuario quiere recordar información suelta. Usar para texto informativo que no es una tarea específica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenido": {
                        "type": "string",
                        "description": "Contenido de la nota a guardar"
                    },
                    "categoria": {
                        "type": "string",
                        "enum": ["general", "trabajo", "personal", "ideas", "estudio"],
                        "description": "Categoría de la nota para organización"
                    }
                },
                "required": ["contenido"]
            }
        }
    },
    
    "listar_notas": {
        "type": "function",
        "function": {
            "name": "listar_notas",
            "description": "Mostrar las notas guardadas del usuario. Usar cuando pregunten por sus notas, anotaciones guardadas, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "enum": ["general", "trabajo", "personal", "ideas", "estudio"],
                        "description": "Filtrar por categoría específica"
                    }
                }
            }
        }
    },
    
    "buscar_notas": {
        "type": "function",
        "function": {
            "name": "buscar_notas",
            "description": "Buscar notas por contenido específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto_busqueda": {
                        "type": "string",
                        "description": "Texto a buscar en las notas"
                    }
                },
                "required": ["texto_busqueda"]
            }
        }
    },
    
    "eliminar_nota": {
        "type": "function",
        "function": {
            "name": "eliminar_nota",
            "description": "Eliminar una nota específica por su ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "nota_id": {
                        "type": "integer",
                        "description": "ID de la nota a eliminar"
                    }
                },
                "required": ["nota_id"]
            }
        }
    }
}