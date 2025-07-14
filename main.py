#!/usr/bin/env python3
"""
Nelida Assistant - Bot de Telegram con IA
Secretaria personal inteligente
"""
import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta
from loguru import logger
import re

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar DESPUÉS de cargar las variables de entorno
from src.utils.bot_logger import bot_logger
from src.ai.simple_ai import SimpleAI
from src.database.models import recordatorio_model
from src.functions.recordatorios import crear_recordatorio, listar_recordatorios, completar_recordatorio, RECORDATORIO_FUNCTIONS
from src.functions.busquedas import buscar_en_internet, obtener_contenido_pagina, BUSQUEDA_FUNCTIONS
from src.functions.fecha_tiempo import obtener_fecha_actual, FECHA_FUNCTIONS
from src.functions.rss_feeds import obtener_noticias_hoy, obtener_noticias_categoria, RSS_FUNCTIONS
from src.functions.tareas import crear_tarea, crear_tareas_multiples, listar_tareas, completar_tareas_multiples, buscar_tareas, TAREA_FUNCTIONS
from src.functions.notificaciones import NotificationScheduler

class NelidaBot:
    def __init__(self):
        # Configurar OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        self.ai = SimpleAI(openai_key) if openai_key else None
        
        # Configurar scheduler de notificaciones
        self.scheduler = None
        self.setup_notification_scheduler()
        
        # Registrar funciones de recordatorios si AI está disponible
        if self.ai:
            self.setup_ai_functions()
        
        print(f"🤖 Nelida Assistant inicializada")
        print(f"🧠 OpenAI: {'✅ Conectado' if self.ai else '❌ No configurado'}")
        print(f"🎭 Personalidad: {'❌ Pendiente configuración' if not (self.ai and self.ai.has_personality()) else '✅ Configurada'}")
        print(f"🔧 Funciones: {'✅ Recordatorios + Búsquedas + RSS + Fecha/Tiempo + Tareas registradas' if self.ai else '❌ Sin funciones'}")
        print(f"🕐 Notificaciones: {'✅ Programadas' if self.scheduler else '❌ No configuradas'}")
    
    def setup_notification_scheduler(self):
        """Configurar el scheduler de notificaciones"""
        try:
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            admin_user_id = os.getenv('ADMIN_USER_ID')
            
            if token and admin_user_id:
                self.scheduler = NotificationScheduler(
                    bot_token=token,
                    admin_user_id=int(admin_user_id)
                )
                logger.info("✅ Scheduler de notificaciones configurado")
            else:
                logger.warning("⚠️ No se pudo configurar scheduler: faltan TELEGRAM_BOT_TOKEN o ADMIN_USER_ID")
                
        except Exception as e:
            logger.error(f"❌ Error configurando scheduler: {e}")
            self.scheduler = None
    
    def setup_ai_functions(self):
        """Registra todas las funciones disponibles para Nélida"""
        # Registrar funciones de recordatorios
        self.ai.register_function("crear_recordatorio", crear_recordatorio, RECORDATORIO_FUNCTIONS["crear_recordatorio"])
        self.ai.register_function("listar_recordatorios", listar_recordatorios, RECORDATORIO_FUNCTIONS["listar_recordatorios"])
        self.ai.register_function("completar_recordatorio", completar_recordatorio, RECORDATORIO_FUNCTIONS["completar_recordatorio"])
        
        # Registrar funciones de búsqueda
        self.ai.register_function("buscar_en_internet", buscar_en_internet, BUSQUEDA_FUNCTIONS["buscar_en_internet"])
        self.ai.register_function("obtener_contenido_pagina", obtener_contenido_pagina, BUSQUEDA_FUNCTIONS["obtener_contenido_pagina"])
        
        # Registrar funciones de fecha/tiempo
        self.ai.register_function("obtener_fecha_actual", obtener_fecha_actual, FECHA_FUNCTIONS["obtener_fecha_actual"])
        
        # Registrar funciones RSS
        self.ai.register_function("obtener_noticias_hoy", obtener_noticias_hoy, RSS_FUNCTIONS["obtener_noticias_hoy"])
        self.ai.register_function("obtener_noticias_categoria", obtener_noticias_categoria, RSS_FUNCTIONS["obtener_noticias_categoria"])
        
        # Registrar funciones de tareas
        self.ai.register_function("crear_tarea", crear_tarea, TAREA_FUNCTIONS["crear_tarea"])
        self.ai.register_function("crear_tareas_multiples", crear_tareas_multiples, TAREA_FUNCTIONS["crear_tareas_multiples"])
        self.ai.register_function("listar_tareas", listar_tareas, TAREA_FUNCTIONS["listar_tareas"])
        self.ai.register_function("completar_tareas_multiples", completar_tareas_multiples, TAREA_FUNCTIONS["completar_tareas_multiples"])
        self.ai.register_function("buscar_tareas", buscar_tareas, TAREA_FUNCTIONS["buscar_tareas"])
        
        logger.info("Funciones de recordatorios, búsquedas, fecha/tiempo, RSS y tareas registradas para Nélida")
    
    def should_use_ai(self, message: str) -> bool:
        """
        Decide si usar OpenAI o respuesta simple
        
        Por ahora lógica básica:
        - "ping" -> respuesta simple
        - Comandos de recordatorios -> respuesta simple
        - Todo lo demás -> OpenAI (si está disponible)
        """
        simple_responses = ["ping", "test", "prueba"]
        recordatorio_commands = ["crear:", "listar", "completar", "pendientes"]
        
        message_lower = message.lower().strip()
        
        # Verificar comandos simples
        if message_lower in simple_responses:
            return False
            
        # Verificar comandos de recordatorios
        for cmd in recordatorio_commands:
            if message_lower.startswith(cmd):
                return False
        
        return True
    
    def parse_fecha_simple(self, texto: str) -> datetime:
        """
        Parser básico de fechas - por ahora muy simple
        """
        now = datetime.now()
        texto_lower = texto.lower()
        
        if "mañana" in texto_lower:
            return now + timedelta(days=1)
        elif "hoy" in texto_lower:
            return now + timedelta(hours=1)  # 1 hora desde ahora
        elif "semana" in texto_lower or "próxima semana" in texto_lower:
            return now + timedelta(days=7)
        else:
            # Por defecto, mañana
            return now + timedelta(days=1)
    
    def handle_recordatorio_commands(self, message: str, user_id: int, username: str) -> str:
        """Maneja comandos específicos de recordatorios"""
        message_lower = message.lower().strip()
        
        try:
            # Comando: crear recordatorio
            if message_lower.startswith("crear:"):
                contenido = message[6:].strip()  # Quitar "crear:"
                if not contenido:
                    return "❌ Necesito que me digas qué recordar. Ejemplo: crear: llamar al médico mañana"
                
                # Parser básico de fecha
                fecha_recordatorio = self.parse_fecha_simple(contenido)
                prioridad = "media"  # Por defecto
                
                # Crear recordatorio
                recordatorio_id = recordatorio_model.crear(
                    contenido=contenido,
                    fecha_recordatorio=fecha_recordatorio,
                    user_id=user_id,
                    prioridad=prioridad
                )
                
                bot_logger.log_function_call(user_id, username, "crear_recordatorio", 
                                           success=True, details=f"ID: {recordatorio_id}")
                
                return f"✅ Recordatorio creado con ID {recordatorio_id}\n📅 {contenido}\n🕐 {fecha_recordatorio.strftime('%d/%m/%Y %H:%M')}"
            
            # Comando: listar recordatorios
            elif message_lower == "listar":
                recordatorios = recordatorio_model.listar_por_usuario(user_id)
                
                if not recordatorios:
                    return "📝 No tenés recordatorios guardados."
                
                respuesta = f"📋 Tus recordatorios ({len(recordatorios)}):\n\n"
                for rec in recordatorios:
                    status_emoji = "✅" if rec['status'] == 'completado' else "⏳"
                    prioridad_emoji = {"alta": "🔴", "media": "🟡", "baja": "🟢"}[rec['prioridad']]
                    
                    respuesta += f"{status_emoji} ID {rec['id']}: {rec['contenido']}\n"
                    respuesta += f"   {prioridad_emoji} {rec['prioridad']} - {rec['fecha_recordatorio']}\n\n"
                
                bot_logger.log_function_call(user_id, username, "listar_recordatorios", 
                                           success=True, details=f"{len(recordatorios)} encontrados")
                return respuesta
            
            # Comando: ver solo pendientes
            elif message_lower == "pendientes":
                recordatorios = recordatorio_model.listar_por_usuario(user_id, status="pendiente")
                
                if not recordatorios:
                    return "🎉 ¡No tenés recordatorios pendientes!"
                
                respuesta = f"⏳ Recordatorios pendientes ({len(recordatorios)}):\n\n"
                for rec in recordatorios:
                    prioridad_emoji = {"alta": "🔴", "media": "🟡", "baja": "🟢"}[rec['prioridad']]
                    respuesta += f"📌 ID {rec['id']}: {rec['contenido']}\n"
                    respuesta += f"   {prioridad_emoji} {rec['fecha_recordatorio']}\n\n"
                
                bot_logger.log_function_call(user_id, username, "listar_pendientes", 
                                           success=True, details=f"{len(recordatorios)} pendientes")
                return respuesta
            
            # Comando: completar recordatorio
            elif message_lower.startswith("completar"):
                # Extraer ID: "completar 1" -> ID = 1
                parts = message.split()
                if len(parts) != 2:
                    return "❌ Formato: completar [ID]\nEjemplo: completar 1"
                
                try:
                    recordatorio_id = int(parts[1])
                except ValueError:
                    return "❌ El ID debe ser un número. Ejemplo: completar 1"
                
                # Verificar que el recordatorio existe y es del usuario
                recordatorio = recordatorio_model.obtener_por_id(recordatorio_id)
                if not recordatorio or recordatorio['user_id'] != user_id:
                    return f"❌ No encontré el recordatorio ID {recordatorio_id}"
                
                # Actualizar status
                success = recordatorio_model.actualizar_status(recordatorio_id, "completado")
                
                if success:
                    bot_logger.log_function_call(user_id, username, "completar_recordatorio", 
                                               success=True, details=f"ID: {recordatorio_id}")
                    return f"✅ Recordatorio completado!\n📝 {recordatorio['contenido']}"
                else:
                    return f"❌ Error al completar el recordatorio {recordatorio_id}"
            
            else:
                return "❌ Comando no reconocido. Usa: crear:, listar, pendientes, completar [ID]"
                
        except Exception as e:
            bot_logger.log_function_call(user_id, username, "recordatorio_error", 
                                       success=False, error=str(e))
            return f"❌ Error procesando recordatorio: {str(e)}"
    
    async def start(self, update: Update, context):
        """Comando /start"""
        user = update.effective_user
        
        # Log de sesión
        bot_logger.log_user_session(user.id, user.username, "Comando /start")
        
        if self.ai and self.ai.has_personality():
            # Respuesta con personalidad de Nélida
            welcome_msg = """¡Ay, hola pibe! 👋 Soy Nélida, tu secretaria de toda la vida. 

Ya ando por acá dispuesta a ayudarte con lo que necesites, no importa qué sea. Organizar, buscar, recordarte cosas... lo que haga falta, nene.

🔧 **Estado actual:**
• Todo funcionando: ✅ Como corresponde
• Mi cerebrito conectado: """ + ("✅ Al mango" if self.ai else "❌ Medio dormido") + """

Contame qué necesitás y yo me ocupo. Usá /help si querés ver todo lo que puedo hacer por vos."""
        else:
            # Respuesta técnica sin personalidad
            welcome_msg = """¡Hola! 👋 Soy Nelida, tu secretaria personal.

🔧 **Estado actual:**
• Bot básico: ✅ Funcionando
• OpenAI: """ + ("✅ Conectado" if self.ai else "❌ No configurado") + """
• Personalidad: """ + ("✅ Lista" if (self.ai and self.ai.has_personality()) else "⏳ En desarrollo") + """

Por ahora puedes:
• Escribir "ping" para respuesta simple
• Escribir cualquier otra cosa para usar IA
• Usar /help para más información"""
        
        await update.message.reply_text(welcome_msg)
    
    async def help_command(self, update: Update, context):
        """Comando /help"""
        user = update.effective_user
        bot_logger.log_user_session(user.id, user.username, "Comando /help")
        
        help_text = """🤖 <b>Nelida Assistant - Comandos</b>

/start - Mensaje de bienvenida
/help - Esta ayuda
/status - Estado del sistema

🧠 <b>¡NUEVO! Nélida con Superpoderes:</b>

📰 <b>Noticias RSS Argentinas (¡NUEVO!):</b>
• "¿Qué noticias hay hoy?" → noticias actuales de medios argentinos
• "Noticias de política" → filtro por categoría
• "Últimas noticias" → feeds de Clarín, La Nación, Infobae, Perfil
• ¡Noticias reales de HOY, no de hace un mes!

🔍 <b>Búsquedas en Internet (con sesgo argentino 🇦🇷):</b>
• "Nélida, buscame información sobre Python"
• "¿Se murió algún famoso?" → busca famosos argentinos
• "Restaurantes buenos" → busca en Buenos Aires
• Por defecto prioriza información local argentina

🌤️ <b>Clima y Fechas (¡MEJORADO!):</b>
• "¿Cómo va a estar el clima mañana?"
• "¿Qué día es hoy?"
• "¿Cuál es la fecha de mañana?"
• Ahora con información detallada y fechas precisas

📝 <b>Recordatorios Inteligentes:</b>
• "Recordame llamar al médico el viernes"
• "¿Qué recordatorios tengo pendientes?"
• "Ya llamé al médico" (marca como completado)
• "Anota que tengo reunión mañana"

✅ <b>¡NUEVO! Sistema de Tareas:</b>
• "Tengo que llamar al médico" → agrega tarea automáticamente
• "Anota que tengo que comprar leche"
• "¿Qué tareas tengo pendientes?"
• "Ya llamé al médico y también compré leche" → marca múltiples como completadas
• "Mis pendientes de trabajo" → filtra por categoría

📋 <b>Recordatorios manuales (aún funcionan):</b>
• <code>crear: llamar al médico mañana</code> - Crear recordatorio
• <code>listar</code> - Ver todos los recordatorios
• <code>pendientes</code> - Ver solo los pendientes
• <code>completar 1</code> - Marcar como completado (usar ID)

🔧 <b>Otros comandos:</b>
• "ping" - Respuesta simple
• Cualquier pregunta - Charlar con Nélida

💡 <b>Ejemplos para probar:</b>
• "Buscame restaurantes en Palermo"
• "¿Qué está pasando en el mundo?"
• "Recordame estudiar para el examen el lunes"""
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context):
        """Comando /status"""
        user = update.effective_user
        bot_logger.log_user_session(user.id, user.username, "Comando /status")
        
        # Verificar si Google Search está configurado
        from src.functions.busquedas import google_client
        google_status = "✅ Configurado" if google_client.is_available() else "⚠️ No configurado (usando DuckDuckGo)"
        
        # Estado del scheduler
        scheduler_status = "❌ No configurado"
        if self.scheduler:
            scheduler_status = "✅ Activo" if self.scheduler.is_running else "⏸️ Configurado pero parado"
        
        status = f"""🔍 **Estado del Sistema**

🤖 **Bot**: ✅ Operativo
🧠 **OpenAI**: {"✅ Conectado" if self.ai else "❌ Desconectado"}
🎭 **Personalidad**: {"✅ Configurada" if (self.ai and self.ai.has_personality()) else "⏳ Pendiente"}
📊 **Logging**: ✅ Activo
🔍 **Google Search**: {google_status}
🕐 **Notificaciones**: {scheduler_status}

🔧 **Funcionalidades activas**:
• ✅ Recordatorios con IA
• ✅ Sistema de tareas inteligente (NUEVO)
• ✅ Búsquedas en internet con Google API
• ✅ RSS feeds de medios argentinos
• ✅ Validación de fechas y tiempo
• ✅ Conversaciones naturales
• ✅ Notificaciones programadas (10:20-10:40 AM)

📁 **Logs disponibles**: logs/bot_actions.log
🔢 **Versión**: 5.0 (con notificaciones automáticas!)"""
        
        await update.message.reply_text(status)
    
    async def test_notification_command(self, update: Update, context):
        """Comando para probar notificaciones"""
        user = update.effective_user
        
        # Solo permitir al admin
        if str(user.id) != os.getenv('ADMIN_USER_ID'):
            await update.message.reply_text("❌ Solo el administrador puede usar este comando.")
            return
        
        if not self.scheduler:
            await update.message.reply_text("❌ Scheduler de notificaciones no está configurado.")
            return
        
        await update.message.reply_text("🧪 Enviando notificación de prueba...")
        
        success = self.scheduler.send_test_notification()
        
        if success:
            await update.message.reply_text("✅ Notificación de prueba enviada correctamente.")
        else:
            await update.message.reply_text("❌ Error enviando notificación de prueba.")
    
    async def handle_message(self, update: Update, context):
        """Maneja todos los mensajes de texto"""
        user = update.effective_user
        message_text = update.message.text
        username = user.username or "sin_username"
        
        try:
            # Decidir si usar respuesta simple, recordatorios o IA
            if not self.should_use_ai(message_text):
                # Comandos simples o recordatorios
                message_lower = message_text.lower().strip()
                
                if message_lower == "ping":
                    response = "pong"
                    bot_logger.log_simple_response(user.id, username, message_text, response)
                elif any(message_lower.startswith(cmd) for cmd in ["crear:", "listar", "completar", "pendientes"]):
                    # Comandos de recordatorios
                    response = self.handle_recordatorio_commands(message_text, user.id, username)
                else:
                    response = f"Recibí: '{message_text}'. Probá: ping, crear:, listar, pendientes, completar [ID]"
                    bot_logger.log_simple_response(user.id, username, message_text, response)
                    
            elif self.ai:
                # Usar OpenAI con function calling
                response = await self.ai.get_response(message_text, user.id, use_personality=True)
                bot_logger.log_ai_response(user.id, username, message_text, success=True)
                
            else:
                # Sin IA configurada
                response = "🤖 OpenAI no está configurado. Por ahora solo puedo responder comandos básicos."
                bot_logger.log_simple_response(user.id, username, message_text, response)
            
            await update.message.reply_text(response)
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {e}"
            bot_logger.log_ai_response(user.id, username, message_text, success=False, error=str(e))
            
            await update.message.reply_text(
                "¡Ups! Tuve un problemita. ¿Podrías intentarlo de nuevo? 🤔"
            )

def main():
    """Función principal"""
    # Verificar token de Telegram
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado en .env")
        return
    
    print("🤖 Iniciando Nelida Assistant...")
    
    # Crear bot
    bot = NelidaBot()
    
    # Crear aplicación
    app = ApplicationBuilder().token(token).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("status", bot.status_command))
    app.add_handler(CommandHandler("test_notification", bot.test_notification_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Iniciar scheduler de notificaciones
    if bot.scheduler:
        bot.scheduler.start()
        print("🕐 Scheduler de notificaciones iniciado")
    
    print("✅ Bot iniciado. Presiona Ctrl+C para detener.")
    print("📊 Logs en: logs/bot_actions.log")
    
    # Ejecutar bot
    try:
        app.run_polling(drop_pending_updates=True)
    finally:
        # Detener scheduler al cerrar
        if bot.scheduler:
            bot.scheduler.stop()
            print("🛑 Scheduler detenido")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Nelida se va a descansar")
    except Exception as e:
        print(f"💥 Error: {e}")