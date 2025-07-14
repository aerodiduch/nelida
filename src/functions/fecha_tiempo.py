"""
Funciones relacionadas con fechas y tiempo para function calling con OpenAI
"""
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any

from ..utils.bot_logger import bot_logger

def obtener_fecha_actual(user_id: int = None) -> Dict[str, Any]:
    """
    Obtener la fecha y hora actual en Argentina
    
    Args:
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        # Timezone de Argentina
        tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora = datetime.now(tz_argentina)
        
        # Formato legible
        fecha_formateada = ahora.strftime("%A %d de %B de %Y")
        hora_formateada = ahora.strftime("%H:%M")
        
        # Día de mañana
        mañana = ahora + timedelta(days=1)
        mañana_formateada = mañana.strftime("%A %d de %B de %Y")
        
        # Traducir días al español
        dias_es = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        
        meses_es = {
            'January': 'enero', 'February': 'febrero', 'March': 'marzo',
            'April': 'abril', 'May': 'mayo', 'June': 'junio',
            'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
            'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
        }
        
        # Aplicar traducciones
        for en, es in dias_es.items():
            fecha_formateada = fecha_formateada.replace(en, es)
            mañana_formateada = mañana_formateada.replace(en, es)
            
        for en, es in meses_es.items():
            fecha_formateada = fecha_formateada.replace(en, es)
            mañana_formateada = mañana_formateada.replace(en, es)
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_fecha_actual",
            success=True, details=f"Fecha: {fecha_formateada}"
        )
        
        return {
            "success": True,
            "fecha_actual": fecha_formateada,
            "hora_actual": hora_formateada,
            "fecha_mañana": mañana_formateada,
            "timestamp": ahora.timestamp(),
            "timezone": "America/Argentina/Buenos_Aires"
        }
        
    except Exception as e:
        error_msg = str(e)
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_fecha_actual",
            success=False, error=error_msg
        )
        
        return {
            "success": False,
            "error": f"Error obteniendo fecha: {error_msg}"
        }

# Definición para OpenAI Function Calling
FECHA_FUNCTIONS = {
    "obtener_fecha_actual": {
        "type": "function",
        "function": {
            "name": "obtener_fecha_actual",
            "description": "Obtener la fecha y hora actual en Argentina. Usar cuando necesites saber qué día es hoy, qué día será mañana, o para validar fechas relativas como 'mañana', 'hoy', etc.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
}