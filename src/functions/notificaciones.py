"""
Sistema de notificaciones programadas para Nelida Assistant
"""
import os
import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger
from telegram import Bot
from telegram.error import TelegramError

from ..database.models import tarea_model

class NotificationScheduler:
    """Scheduler para notificaciones automáticas"""
    
    def __init__(self, bot_token: str, admin_user_id: int):
        self.bot = Bot(token=bot_token)
        self.admin_user_id = admin_user_id
        self.notification_start = os.getenv('NOTIFICATION_TIME_START', '10:20')
        self.notification_end = os.getenv('NOTIFICATION_TIME_END', '10:40')
        self.is_running = False
        self.scheduler_thread = None
        
        logger.info(f"Scheduler configurado para notificar entre {self.notification_start} y {self.notification_end}")
    
    def start(self):
        """Iniciar el scheduler en un hilo separado"""
        if self.is_running:
            logger.warning("Scheduler ya está ejecutándose")
            return
        
        self.is_running = True
        
        # Programar notificación diaria
        schedule.every().day.at(self.notification_start).do(self._send_daily_tasks_notification)
        
        # Iniciar el scheduler en un hilo separado
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("🕐 Scheduler de notificaciones iniciado")
    
    def stop(self):
        """Detener el scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("🛑 Scheduler de notificaciones detenido")
    
    def _run_scheduler(self):
        """Ejecutar el scheduler en bucle"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Verificar cada 30 segundos
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(60)  # En caso de error, esperar más tiempo
    
    def _send_daily_tasks_notification(self):
        """Enviar notificación diaria con tareas pendientes"""
        try:
            # Verificar que estamos en el rango de tiempo correcto
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            start_time = datetime.strptime(self.notification_start, '%H:%M').time()
            end_time = datetime.strptime(self.notification_end, '%H:%M').time()
            current_time_obj = datetime.strptime(current_time, '%H:%M').time()
            
            if not (start_time <= current_time_obj <= end_time):
                logger.info(f"Fuera del rango de notificación. Hora actual: {current_time}")
                return
            
            # Obtener tareas pendientes
            tareas_pendientes = tarea_model.listar_por_usuario(
                user_id=self.admin_user_id,
                status="pendiente"
            )
            
            # Crear mensaje
            mensaje = self._crear_mensaje_tareas_pendientes(tareas_pendientes)
            
            # Enviar mensaje
            asyncio.run(self._send_message(mensaje))
            
            logger.info(f"✅ Notificación de tareas enviada a las {current_time}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación diaria: {e}")
    
    def _crear_mensaje_tareas_pendientes(self, tareas: list) -> str:
        """Crear mensaje con resumen de tareas pendientes"""
        if not tareas:
            return "🎉 ¡Buen día! No tenés tareas pendientes por ahora. ¡Perfecto para empezar el día tranquilo!"
        
        # Contar tareas por prioridad
        alta_prioridad = [t for t in tareas if t['prioridad'] == 'alta']
        media_prioridad = [t for t in tareas if t['prioridad'] == 'media']
        baja_prioridad = [t for t in tareas if t['prioridad'] == 'baja']
        
        # Contar tareas por categoría
        categorias = {}
        for tarea in tareas:
            cat = tarea['categoria']
            if cat not in categorias:
                categorias[cat] = 0
            categorias[cat] += 1
        
        # Construir mensaje
        mensaje = f"🌅 **Buenos días! Resumen de tareas pendientes**\n\n"
        mensaje += f"📊 **Total: {len(tareas)} tareas**\n\n"
        
        # Resumen por prioridad
        if alta_prioridad:
            mensaje += f"🔴 **Urgentes ({len(alta_prioridad)}):**\n"
            for tarea in alta_prioridad[:3]:  # Mostrar máximo 3
                mensaje += f"• {tarea['contenido']}\n"
            if len(alta_prioridad) > 3:
                mensaje += f"• ... y {len(alta_prioridad) - 3} más\n"
            mensaje += "\n"
        
        if media_prioridad:
            mensaje += f"🟡 **Importantes ({len(media_prioridad)}):**\n"
            for tarea in media_prioridad[:2]:  # Mostrar máximo 2
                mensaje += f"• {tarea['contenido']}\n"
            if len(media_prioridad) > 2:
                mensaje += f"• ... y {len(media_prioridad) - 2} más\n"
            mensaje += "\n"
        
        if baja_prioridad:
            mensaje += f"🟢 **Para cuando puedas ({len(baja_prioridad)})**\n\n"
        
        # Resumen por categorías
        if categorias:
            mensaje += "📁 **Por categorías:**\n"
            for categoria, cantidad in categorias.items():
                emoji_cat = {
                    'trabajo': '💼',
                    'casa': '🏠',
                    'salud': '🏥',
                    'estudios': '📚',
                    'general': '📝'
                }.get(categoria, '📝')
                mensaje += f"{emoji_cat} {categoria.title()}: {cantidad}\n"
        
        mensaje += f"\n💡 **Tip:** Empezá por las urgentes. ¡Vos podés!"
        
        return mensaje
    
    async def _send_message(self, message: str):
        """Enviar mensaje por Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.admin_user_id,
                text=message,
                parse_mode='Markdown'
            )
        except TelegramError as e:
            logger.error(f"Error enviando mensaje de Telegram: {e}")
            # Intentar sin markdown
            try:
                await self.bot.send_message(
                    chat_id=self.admin_user_id,
                    text=message.replace('*', '').replace('`', '')
                )
            except TelegramError as e2:
                logger.error(f"Error enviando mensaje sin formato: {e2}")
    
    def send_test_notification(self) -> bool:
        """Enviar notificación de prueba"""
        try:
            tareas_pendientes = tarea_model.listar_por_usuario(
                user_id=self.admin_user_id,
                status="pendiente"
            )
            
            mensaje = "🧪 **NOTIFICACIÓN DE PRUEBA**\n\n"
            mensaje += self._crear_mensaje_tareas_pendientes(tareas_pendientes)
            mensaje += f"\n\n⏰ Enviado a las {datetime.now().strftime('%H:%M:%S')}"
            
            asyncio.run(self._send_message(mensaje))
            logger.info("✅ Notificación de prueba enviada")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación de prueba: {e}")
            return False