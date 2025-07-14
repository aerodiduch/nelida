#!/bin/bash

# Script de deploy para Nelida Assistant con Docker
# Uso: ./deploy.sh [start|stop|restart|logs|status]

set -e

PROJECT_NAME="nelida-assistant"
COMPOSE_FILE="docker-compose.yml"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🤖 Nelida Assistant - Script de Deploy${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start    - Iniciar el bot"
    echo "  stop     - Detener el bot"
    echo "  restart  - Reiniciar el bot"
    echo "  logs     - Mostrar logs en tiempo real"
    echo "  status   - Mostrar estado del container"
    echo "  build    - Reconstruir imagen Docker"
    echo "  setup    - Configuración inicial"
    echo "  help     - Mostrar esta ayuda"
    echo ""
}

# Verificar que existe docker-compose
check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose no está instalado${NC}"
        exit 1
    fi
}

# Verificar archivo .env
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo -e "${BLUE}💡 Copiando .env.example a .env${NC}"
        cp .env.example .env
        echo -e "${RED}🔧 IMPORTANTE: Edita el archivo .env con tus configuraciones antes de continuar${NC}"
        exit 1
    fi
}

# Función para iniciar el bot
start_bot() {
    echo -e "${GREEN}🚀 Iniciando Nelida Assistant...${NC}"
    check_requirements
    check_env
    
    # Crear directorios si no existen
    mkdir -p data logs
    
    # Iniciar con docker-compose
    docker-compose up -d
    
    echo -e "${GREEN}✅ Bot iniciado exitosamente${NC}"
    echo -e "${BLUE}📊 Para ver logs: ./deploy.sh logs${NC}"
}

# Función para detener el bot
stop_bot() {
    echo -e "${YELLOW}⏹️  Deteniendo Nelida Assistant...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Bot detenido${NC}"
}

# Función para reiniciar el bot
restart_bot() {
    echo -e "${BLUE}🔄 Reiniciando Nelida Assistant...${NC}"
    stop_bot
    sleep 2
    start_bot
}

# Función para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Mostrando logs de Nelida Assistant...${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para salir${NC}"
    docker-compose logs -f $PROJECT_NAME
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}📊 Estado de Nelida Assistant:${NC}"
    echo ""
    
    # Estado del container
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}🟢 Estado: EJECUTÁNDOSE${NC}"
    else
        echo -e "${RED}🔴 Estado: DETENIDO${NC}"
    fi
    
    # Información del container
    docker-compose ps
    
    echo ""
    echo -e "${BLUE}📁 Archivos de datos:${NC}"
    ls -la data/ 2>/dev/null || echo "Directorio data/ no existe"
    
    echo ""
    echo -e "${BLUE}📝 Archivos de logs:${NC}"
    ls -la logs/ 2>/dev/null || echo "Directorio logs/ no existe"
}

# Función para reconstruir imagen
build_image() {
    echo -e "${BLUE}🔨 Reconstruyendo imagen Docker...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}✅ Imagen reconstruida${NC}"
}

# Función de configuración inicial
setup_project() {
    echo -e "${BLUE}⚙️  Configuración inicial de Nelida Assistant${NC}"
    
    check_requirements
    
    # Crear directorios
    mkdir -p data logs
    echo -e "${GREEN}✅ Directorios creados${NC}"
    
    # Verificar archivo .env
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado desde template${NC}"
        echo -e "${RED}🔧 EDITA el archivo .env con tus configuraciones:${NC}"
        echo "   - TELEGRAM_BOT_TOKEN"
        echo "   - OPENAI_API_KEY"
        echo "   - ADMIN_USER_ID"
    else
        echo -e "${YELLOW}⚠️  Archivo .env ya existe${NC}"
    fi
    
    # Construir imagen
    echo -e "${BLUE}🔨 Construyendo imagen Docker...${NC}"
    docker-compose build
    
    echo -e "${GREEN}✅ Configuración inicial completada${NC}"
    echo -e "${BLUE}🚀 Para iniciar: ./deploy.sh start${NC}"
}

# Main script
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_image
        ;;
    setup)
        setup_project
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac