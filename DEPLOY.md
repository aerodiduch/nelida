# 🚀 Guía de Deploy - Nelida Assistant con Docker

Esta guía te ayudará a deployar tu asistente Nelida en tu servidor usando Docker de forma rápida y segura.

## 📋 Prerrequisitos

- Docker y Docker Compose instalados en tu servidor
- Token de bot de Telegram (obtenido de @BotFather)
- API Key de OpenAI
- Tu Telegram User ID (para recibir notificaciones)

## 🔧 Configuración Inicial

### 1. Clonar/Subir el proyecto a tu servidor

```bash
# Si usas git
git clone <tu-repo> nelida-assistant
cd nelida-assistant

# O subir archivos manualmente via scp/sftp
```

### 2. Configurar variables de entorno

```bash
# Copiar template de configuración
cp .env.example .env

# Editar con tus configuraciones
nano .env
```

**Variables obligatorias a configurar:**
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
OPENAI_API_KEY=tu_api_key_aqui
ADMIN_USER_ID=tu_user_id_aqui
```

### 3. Configurar notificaciones (opcional)

```env
# Horario de notificaciones matutinas
NOTIFICATION_TIME_START=10:20
NOTIFICATION_TIME_END=10:40
TZ=America/Argentina/Buenos_Aires
```

## 🚀 Deploy Rápido

### Método 1: Script automatizado (Recomendado)

```bash
# Hacer ejecutable el script
chmod +x deploy.sh

# Configuración inicial (primera vez)
./deploy.sh setup

# Iniciar el bot
./deploy.sh start
```

### Método 2: Docker Compose manual

```bash
# Construir imagen
docker-compose build

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 📊 Comandos de Gestión

### Scripts de deploy

```bash
./deploy.sh start     # Iniciar bot
./deploy.sh stop      # Detener bot
./deploy.sh restart   # Reiniciar bot
./deploy.sh logs      # Ver logs en tiempo real
./deploy.sh status    # Ver estado del sistema
./deploy.sh build     # Reconstruir imagen
```

### Docker Compose directo

```bash
docker-compose up -d              # Iniciar
docker-compose down               # Detener
docker-compose restart           # Reiniciar
docker-compose logs -f nelida-assistant  # Logs
docker-compose ps                # Estado
```

## 🔍 Verificación

### 1. Verificar que el bot está corriendo

```bash
# Método 1: Script
./deploy.sh status

# Método 2: Docker directo
docker-compose ps
```

### 2. Verificar logs

```bash
# Logs del container
./deploy.sh logs

# Logs de la aplicación
tail -f logs/nelida.log
```

### 3. Probar el bot

1. Envía `/start` a tu bot en Telegram
2. Verifica el comando `/status`
3. Prueba con `/test_notification` (solo admin)

## 🕐 Sistema de Notificaciones

### Configuración

El bot enviará automáticamente un resumen de tareas pendientes:
- **Horario**: Entre 10:20 y 10:40 AM (configurable)
- **Destinatario**: Solo el admin (ADMIN_USER_ID)
- **Contenido**: Lista de tareas por prioridad y categoría

### Comandos relacionados

```bash
/test_notification  # Probar notificación (solo admin)
/status            # Ver estado del scheduler
```

## 📁 Estructura de Archivos

```
nelida-assistant/
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Orquestación
├── deploy.sh              # Script de deploy
├── docker-entrypoint.sh   # Script de inicio
├── .env                   # Variables de entorno (TU CONFIGURACIÓN)
├── .env.example          # Template de variables
├── data/                 # Base de datos (persistente)
├── logs/                 # Logs de aplicación (persistente)
└── src/                  # Código fuente
```

## 🔧 Mantenimiento

### Actualizar el bot

```bash
# Detener bot actual
./deploy.sh stop

# Actualizar código (git pull o subir archivos)
git pull origin main

# Reconstruir imagen
./deploy.sh build

# Iniciar nuevamente
./deploy.sh start
```

### Backup de datos

```bash
# Backup de base de datos
cp data/nelida.db backup/nelida_$(date +%Y%m%d).db

# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/ .env
```

### Ver logs históricos

```bash
# Logs de aplicación
cat logs/nelida.log

# Logs de acciones del bot
cat logs/bot_actions.log

# Logs del container Docker
docker-compose logs nelida-assistant
```

## 🚨 Troubleshooting

### Bot no inicia

1. **Verificar variables de entorno**:
   ```bash
   cat .env
   ```

2. **Verificar logs**:
   ```bash
   ./deploy.sh logs
   ```

3. **Verificar conectividad**:
   ```bash
   curl -s https://api.telegram.org/botTU_TOKEN/getMe
   ```

### Notificaciones no llegan

1. **Verificar ADMIN_USER_ID**:
   - Debe ser tu Telegram User ID (número)
   - Obtenerlo con @userinfobot

2. **Verificar horario**:
   - Las notificaciones solo se envían entre NOTIFICATION_TIME_START y NOTIFICATION_TIME_END

3. **Probar manualmente**:
   ```bash
   # En Telegram, enviar:
   /test_notification
   ```

### Container se reinicia constantemente

1. **Verificar recursos**:
   ```bash
   docker stats nelida-assistant
   ```

2. **Verificar logs de error**:
   ```bash
   docker-compose logs --tail=50 nelida-assistant
   ```

## 🔐 Seguridad

- ✅ El container corre con usuario no-root
- ✅ Variables sensibles en archivo .env (no commiteado)
- ✅ Logs rotativos para evitar llenar disco
- ✅ Healthcheck para monitoreo automático
- ✅ Solo admin puede usar comandos de gestión

## 📈 Monitoreo

### Healthcheck automático

Docker revisa cada 30s que el bot esté funcionando.

### Logs automáticos

- **Rotación**: Máximo 3 archivos de 50MB cada uno
- **Ubicación**: `logs/nelida.log` y `logs/bot_actions.log`

### Comandos útiles

```bash
# Ver uso de recursos
docker stats nelida-assistant

# Ver espacio en disco
df -h

# Ver tamaño de logs
du -sh logs/
```

---

## 🎉 ¡Listo!

Tu Nelida Assistant ya está deployado y funcionando con:

- ✅ **Containerización completa** con Docker
- ✅ **Auto-reinicio** en caso de fallos
- ✅ **Notificaciones programadas** de tareas pendientes
- ✅ **Persistencia de datos** en volumes
- ✅ **Scripts de gestión** automatizados
- ✅ **Logs monitoreados** y rotativos

**Para usar mañana en el trabajo**: El bot te enviará automáticamente entre las 10:20 y 10:40 AM un resumen de todas tus tareas pendientes organizadas por prioridad y categoría. ¡Perfecto para empezar el día organizado!