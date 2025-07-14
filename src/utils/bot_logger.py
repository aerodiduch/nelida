"""
Sistema de logging específico para acciones del bot
"""
import os
from datetime import datetime
from loguru import logger

class BotLogger:
    """Logger especializado para acciones del bot"""
    
    def __init__(self):
        self.setup_bot_logger()
    
    def setup_bot_logger(self):
        """Configura logger específico para acciones del bot"""
        # Crear directorio de logs si no existe
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Configurar logger específico para acciones del bot
        logger.add(
            "logs/bot_actions.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            rotation="10 MB",
            retention="30 days",
            level="INFO",
            filter=lambda record: record["extra"].get("bot_action", False)
        )
    
    def log_simple_response(self, user_id: int, username: str, input_msg: str, output_msg: str):
        """Log para respuestas simples (sin IA)"""
        logger.bind(bot_action=True).info(
            f"Usuario {user_id} (@{username}) - RESPUESTA_SIMPLE - Input: '{input_msg}' -> Output: '{output_msg}'"
        )
    
    def log_ai_response(self, user_id: int, username: str, input_msg: str, success: bool = True, error: str = None):
        """Log para respuestas usando OpenAI"""
        if success:
            logger.bind(bot_action=True).info(
                f"Usuario {user_id} (@{username}) - OPENAI_USADO - Input: '{input_msg}' - Éxito"
            )
        else:
            logger.bind(bot_action=True).error(
                f"Usuario {user_id} (@{username}) - OPENAI_ERROR - Input: '{input_msg}' - Error: {error}"
            )
    
    def log_function_call(self, user_id: int, username: str, function_name: str, success: bool = True, error: str = None, details: str = None):
        """Log para llamadas a funciones específicas"""
        status = "Éxito" if success else f"Error: {error}"
        details_str = f" - Detalles: {details}" if details else ""
        
        logger.bind(bot_action=True).info(
            f"Usuario {user_id} (@{username}) - FUNCIÓN_{function_name.upper()} - {status}{details_str}"
        )
    
    def log_user_session(self, user_id: int, username: str, action: str):
        """Log para acciones de sesión (inicio, comandos, etc.)"""
        logger.bind(bot_action=True).info(
            f"Usuario {user_id} (@{username}) - SESIÓN - {action}"
        )

# Instancia global
bot_logger = BotLogger()