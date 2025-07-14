#!/bin/bash
set -e

# Script de entrada para Nelida Assistant Docker container

echo "🤖 Iniciando Nelida Assistant..."

# Crear directorios necesarios si no existen
mkdir -p /app/data
mkdir -p /app/logs

# Verificar variables de entorno críticas
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN no está configurado"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY no está configurado"
    exit 1
fi

echo "✅ Variables de entorno verificadas"

# Configurar zona horaria si está definida
if [ ! -z "$TZ" ]; then
    echo "🕐 Configurando zona horaria: $TZ"
    export TZ="$TZ"
fi

# Verificar conectividad básica
echo "🌐 Verificando conectividad..."
if ! curl -s --max-time 10 https://api.telegram.org > /dev/null; then
    echo "⚠️  Advertencia: No se pudo conectar a Telegram API"
else
    echo "✅ Conectividad verificada"
fi

# Validar estructura de directorios
echo "📁 Verificando estructura de directorios..."
if [ ! -d "/app/src" ]; then
    echo "❌ Error: Directorio /app/src no encontrado"
    exit 1
fi

# Ejecutar comando pasado como argumento
echo "🚀 Ejecutando: $@"
exec "$@"