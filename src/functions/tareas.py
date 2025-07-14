"""
Funciones para manejo de tareas con lenguaje natural
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
from ..database.models import tarea_model

async def crear_tareas_multiples(texto_tareas: str, user_id: int) -> Dict[str, Any]:
    """
    Crear múltiples tareas desde una sola frase
    
    Args:
        texto_tareas: Texto que contiene múltiples tareas separadas por conjunciones
        user_id: ID del usuario de Telegram
    
    Returns:
        Dict con información de las tareas creadas
    """
    try:
        # Extraer tareas individuales del texto
        tareas_individuales = extraer_tareas_multiples(texto_tareas)
        
        if not tareas_individuales:
            return {
                "success": False,
                "message": "No pude identificar tareas específicas en el texto, nene"
            }
        
        tareas_creadas = []
        errores = []
        
        for tarea_texto in tareas_individuales:
            # Detectar prioridad y categoría para cada tarea individual
            prioridad = detectar_prioridad(tarea_texto)
            categoria = detectar_categoria(tarea_texto)
            
            try:
                tarea_id = tarea_model.crear(
                    contenido=tarea_texto,
                    user_id=user_id,
                    prioridad=prioridad,
                    categoria=categoria
                )
                
                tareas_creadas.append({
                    "id": tarea_id,
                    "contenido": tarea_texto,
                    "prioridad": prioridad,
                    "categoria": categoria
                })
                
            except Exception as e:
                errores.append(f"Error creando '{tarea_texto}': {str(e)}")
        
        return {
            "success": len(tareas_creadas) > 0,
            "tareas_creadas": tareas_creadas,
            "total_creadas": len(tareas_creadas),
            "errores": errores,
            "message": f"Se crearon {len(tareas_creadas)} tareas"
        }
        
    except Exception as e:
        logger.error(f"Error creando tareas múltiples: {e}")
        return {
            "success": False,
            "message": f"Error al crear las tareas: {str(e)}"
        }

async def crear_tarea(contenido: str, user_id: int, prioridad: str = "media", 
                     categoria: str = "general") -> Dict[str, Any]:
    """
    Crear una nueva tarea
    
    Args:
        contenido: Texto de la tarea a crear
        user_id: ID del usuario de Telegram
        prioridad: Prioridad de la tarea (alta, media, baja)
        categoria: Categoría para organizar la tarea
    
    Returns:
        Dict con información de la tarea creada
    """
    try:
        # Limpiar contenido
        contenido_limpio = contenido.strip()
        
        if not contenido_limpio:
            return {
                "success": False,
                "message": "No puedo crear una tarea vacía, nene"
            }
        
        # Detectar prioridad en el texto
        prioridad_detectada = detectar_prioridad(contenido_limpio)
        if prioridad_detectada:
            prioridad = prioridad_detectada
        
        # Detectar categoría en el texto
        categoria_detectada = detectar_categoria(contenido_limpio)
        if categoria_detectada:
            categoria = categoria_detectada
        
        # Crear la tarea
        tarea_id = tarea_model.crear(
            contenido=contenido_limpio,
            user_id=user_id,
            prioridad=prioridad,
            categoria=categoria
        )
        
        return {
            "success": True,
            "tarea_id": tarea_id,
            "contenido": contenido_limpio,
            "prioridad": prioridad,
            "categoria": categoria,
            "message": f"Tarea agregada: {contenido_limpio}"
        }
        
    except Exception as e:
        logger.error(f"Error creando tarea: {e}")
        return {
            "success": False,
            "message": f"Error al crear la tarea: {str(e)}"
        }

async def listar_tareas(user_id: int, status: str = "pendiente", 
                       categoria: str = None) -> Dict[str, Any]:
    """
    Listar tareas del usuario
    
    Args:
        user_id: ID del usuario
        status: Estado de las tareas (pendiente, completado, cancelado)
        categoria: Filtrar por categoría específica
    
    Returns:
        Dict con lista de tareas
    """
    try:
        tareas = tarea_model.listar_por_usuario(
            user_id=user_id,
            status=status if status != "todas" else None,
            categoria=categoria
        )
        
        return {
            "success": True,
            "tareas": tareas,
            "total": len(tareas),
            "status_filtro": status,
            "categoria_filtro": categoria
        }
        
    except Exception as e:
        logger.error(f"Error listando tareas: {e}")
        return {
            "success": False,
            "message": f"Error al listar tareas: {str(e)}"
        }

async def completar_tareas_multiples(texto_completado: str, user_id: int) -> Dict[str, Any]:
    """
    Marcar múltiples tareas como completadas basándose en texto libre
    
    Args:
        texto_completado: Texto que describe qué tareas se completaron
        user_id: ID del usuario
    
    Returns:
        Dict con resultados de las tareas completadas
    """
    try:
        # Extraer palabras clave del texto
        palabras_clave = extraer_palabras_clave_tareas(texto_completado)
        
        if not palabras_clave:
            return {
                "success": False,
                "message": "No pude identificar qué tareas completaste, pibe"
            }
        
        # Completar tareas basándose en las palabras clave
        resultado = tarea_model.completar_multiples(palabras_clave, user_id)
        
        return {
            "success": True,
            "completadas": resultado['completadas'],
            "no_encontradas": resultado['no_encontradas'],
            "total_completadas": len(resultado['completadas']),
            "palabras_clave": palabras_clave
        }
        
    except Exception as e:
        logger.error(f"Error completando tareas múltiples: {e}")
        return {
            "success": False,
            "message": f"Error al completar tareas: {str(e)}"
        }

async def buscar_tareas(texto_busqueda: str, user_id: int) -> Dict[str, Any]:
    """
    Buscar tareas por contenido
    
    Args:
        texto_busqueda: Texto a buscar en las tareas
        user_id: ID del usuario
    
    Returns:
        Dict con tareas encontradas
    """
    try:
        tareas = tarea_model.buscar_por_contenido(texto_busqueda, user_id)
        
        return {
            "success": True,
            "tareas": tareas,
            "total": len(tareas),
            "busqueda": texto_busqueda
        }
        
    except Exception as e:
        logger.error(f"Error buscando tareas: {e}")
        return {
            "success": False,
            "message": f"Error al buscar tareas: {str(e)}"
        }

def detectar_prioridad(texto: str) -> str:
    """
    Detectar prioridad en el texto de la tarea
    
    Args:
        texto: Texto de la tarea
    
    Returns:
        Prioridad detectada o None
    """
    texto_lower = texto.lower()
    
    # Palabras para alta prioridad
    alta_prioridad = ["urgente", "importante", "prioritario", "ya", "ahora", "inmediato"]
    if any(palabra in texto_lower for palabra in alta_prioridad):
        return "alta"
    
    # Palabras para baja prioridad
    baja_prioridad = ["después", "cuando pueda", "más tarde", "sin apuro", "tranquilo"]
    if any(palabra in texto_lower for palabra in baja_prioridad):
        return "baja"
    
    return "media"  # Default

def detectar_categoria(texto: str) -> str:
    """
    Detectar categoría en el texto de la tarea
    
    Args:
        texto: Texto de la tarea
    
    Returns:
        Categoría detectada
    """
    texto_lower = texto.lower()
    
    # Categorías de trabajo
    trabajo_keywords = ["trabajo", "oficina", "reunión", "proyecto", "cliente", "jefe", "empresa"]
    if any(palabra in texto_lower for palabra in trabajo_keywords):
        return "trabajo"
    
    # Categorías de casa
    casa_keywords = ["casa", "hogar", "limpiar", "comprar", "cocinar", "familia"]
    if any(palabra in texto_lower for palabra in casa_keywords):
        return "casa"
    
    # Categorías de salud
    salud_keywords = ["médico", "doctor", "dentista", "farmacia", "medicina", "salud"]
    if any(palabra in texto_lower for palabra in salud_keywords):
        return "salud"
    
    # Categorías de estudios
    estudio_keywords = ["estudiar", "examen", "curso", "universidad", "colegio", "tarea"]
    if any(palabra in texto_lower for palabra in estudio_keywords):
        return "estudios"
    
    return "general"  # Default

def extraer_palabras_clave_tareas(texto: str) -> List[str]:
    """
    Extraer palabras clave del texto para identificar tareas completadas
    
    Args:
        texto: Texto que describe las tareas completadas
    
    Returns:
        Lista de palabras clave para buscar tareas
    """
    # Limpiar texto
    texto = texto.lower().strip()
    
    # Palabras de acción que indican completado (las removemos)
    palabras_accion = [
        "ya", "terminé", "completé", "hice", "resolví", "llamé", "fui", 
        "compré", "pagué", "envié", "mandé", "escribí", "finalicé",
        "también", "y", "además", "ahora", "recién"
    ]
    
    # Dividir en frases por conjunciones
    frases = re.split(r'\s+y\s+|\s+también\s+|\s+además\s+|,', texto)
    
    palabras_clave = []
    
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
            
        # Remover palabras de acción del inicio
        palabras = frase.split()
        palabras_filtradas = []
        
        for palabra in palabras:
            if palabra not in palabras_accion:
                palabras_filtradas.append(palabra)
        
        # Si queda algo significativo, agregarlo
        if palabras_filtradas:
            # Intentar extraer el núcleo de la tarea
            nucleo = ' '.join(palabras_filtradas)
            
            # Si es muy corto, agregar palabras individuales importantes
            if len(palabras_filtradas) <= 2:
                palabras_clave.extend(palabras_filtradas)
            else:
                palabras_clave.append(nucleo)
    
    # Filtrar palabras muy cortas o comunes
    palabras_finales = []
    palabras_comunes = ["el", "la", "los", "las", "un", "una", "de", "del", "al", "a", "en", "con", "por", "para"]
    
    for palabra in palabras_clave:
        if len(palabra) > 2 and palabra not in palabras_comunes:
            palabras_finales.append(palabra)
    
    return palabras_finales

def extraer_tareas_multiples(texto: str) -> List[str]:
    """
    Extraer múltiples tareas de un texto separadas por conjunciones
    
    Args:
        texto: Texto que contiene múltiples tareas
    
    Returns:
        Lista de tareas individuales
    """
    # Limpiar texto inicial
    texto = texto.strip()
    
    # Remover frases de introducción comunes
    prefijos_comunes = [
        "tengo que", "debo", "necesito", "me falta", "tengo pendiente",
        "anota que", "recordá que", "apuntá que", "agrega que"
    ]
    
    texto_limpio = texto.lower()
    for prefijo in prefijos_comunes:
        if texto_limpio.startswith(prefijo):
            # Mantener el caso original pero quitar el prefijo
            texto = texto[len(prefijo):].strip()
            break
    
    import re
    
    # Separadores más simples y efectivos
    # Usar comas como separador principal, pero también "también" y "además"
    separadores = [
        r',\s+',  # coma seguida de espacio
        r'\s+también\s+',  # " también "
        r'\s+además\s+',  # " además "
        r';\s*'  # punto y coma
    ]
    
    # Unir separadores con OR
    patron = '|'.join(separadores)
    tareas_raw = re.split(patron, texto, flags=re.IGNORECASE)
    
    # Limpiar cada tarea individual
    tareas_limpias = []
    
    for tarea in tareas_raw:
        tarea = tarea.strip()
        
        # Saltar tareas muy cortas o vacías
        if len(tarea) < 3:
            continue
        
        # Remover palabras de transición comunes al inicio
        palabras_transicion = ["que", "de", "a", "el", "la", "los", "las", "un", "una"]
        palabras_tarea = tarea.split()
        
        # Quitar palabras de transición del inicio
        while palabras_tarea and palabras_tarea[0].lower() in palabras_transicion:
            palabras_tarea.pop(0)
        
        if palabras_tarea:
            tarea_final = ' '.join(palabras_tarea)
            
            # Solo agregar si tiene sentido como tarea
            if len(tarea_final) > 2 and len(palabras_tarea) >= 1:
                tareas_limpias.append(tarea_final)
    
    return tareas_limpias

# Definiciones de funciones para OpenAI Function Calling
TAREA_FUNCTIONS = {
    "crear_tareas_multiples": {
        "type": "function",
        "function": {
            "name": "crear_tareas_multiples",
            "description": "Crear múltiples tareas desde una sola frase cuando el usuario menciona varias cosas que tiene que hacer. Ejemplo: 'tengo que llamar al médico, comprar leche y estudiar matemáticas'",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto_tareas": {
                        "type": "string",
                        "description": "Texto completo que contiene múltiples tareas separadas por conjunciones o comas"
                    }
                },
                "required": ["texto_tareas"]
            }
        }
    },
    
    "crear_tarea": {
        "type": "function",
        "function": {
            "name": "crear_tarea",
            "description": "Crear una nueva tarea/pendiente para el usuario. Usar cuando el usuario dice que quiere anotar, agregar o recordar hacer algo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenido": {
                        "type": "string",
                        "description": "Descripción de la tarea a crear"
                    },
                    "prioridad": {
                        "type": "string",
                        "enum": ["alta", "media", "baja"],
                        "description": "Prioridad de la tarea (alta para urgente, media por defecto, baja para cuando se pueda)"
                    },
                    "categoria": {
                        "type": "string",
                        "enum": ["general", "trabajo", "casa", "salud", "estudios"],
                        "description": "Categoría de la tarea para organización"
                    }
                },
                "required": ["contenido"]
            }
        }
    },
    
    "listar_tareas": {
        "type": "function",
        "function": {
            "name": "listar_tareas",
            "description": "Mostrar las tareas del usuario. Usar cuando pregunten qué tareas tienen, sus pendientes, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pendiente", "completado", "todas"],
                        "description": "Filtrar por estado de las tareas"
                    },
                    "categoria": {
                        "type": "string",
                        "enum": ["general", "trabajo", "casa", "salud", "estudios"],
                        "description": "Filtrar por categoría específica"
                    }
                }
            }
        }
    },
    
    "completar_tareas_multiples": {
        "type": "function",
        "function": {
            "name": "completar_tareas_multiples",
            "description": "Marcar múltiples tareas como completadas cuando el usuario dice que ya hizo varias cosas. Ejemplo: 'ya llamé al médico y también resolví el problema X'",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto_completado": {
                        "type": "string",
                        "description": "Texto completo del usuario describiendo qué tareas completó"
                    }
                },
                "required": ["texto_completado"]
            }
        }
    },
    
    "buscar_tareas": {
        "type": "function",
        "function": {
            "name": "buscar_tareas",
            "description": "Buscar tareas por contenido específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto_busqueda": {
                        "type": "string",
                        "description": "Texto a buscar en las tareas"
                    }
                },
                "required": ["texto_busqueda"]
            }
        }
    }
}