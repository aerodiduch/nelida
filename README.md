# 🤖 Nelida Assistant

Bot de Telegram con IA que funciona como secretaria personal inteligente.

## 🚀 Características

- **Conversaciones inteligentes** con OpenAI GPT-4
- **Function Calling** para ejecutar tareas reales
- **Personalidad única** (Nelida: leal, directa, fumadora 🚬)
- **Funcionalidades de secretaria**:
  - Recordatorios y tareas
  - Búsquedas en internet
  - Envío de emails
  - Gestión de calendario
  - Notas organizadas
  - Consultas del clima

## 📋 Requisitos Previos

1. **Python 3.8+**
2. **API Key de OpenAI**
3. **Bot Token de Telegram** (crear en @BotFather)
4. **Entorno virtual Python** (ya incluido en `venv/`)

## ⚡ Instalación Rápida

1. **Clonar y navegar al proyecto**:
   ```bash
   cd nelida-assistant
   ```

2. **Activar entorno virtual**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # o
   venv\\Scripts\\activate   # Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus tokens
   ```

5. **Ejecutar Nelida**:
   ```bash
   python main.py
   ```

## 🔧 Configuración

### Variables de Entorno Requeridas

Edita el archivo `.env`:

```bash
# OBLIGATORIAS
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
OPENAI_API_KEY=tu_api_key_de_openai

# OPCIONALES (para funciones avanzadas)
ADMIN_USER_ID=tu_telegram_user_id
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
GOOGLE_CLIENT_ID=tu_google_client_id
GOOGLE_CLIENT_SECRET=tu_google_client_secret
```

### Obtener Tokens

1. **Telegram Bot Token**:
   - Habla con @BotFather en Telegram
   - Crea un nuevo bot con `/newbot`
   - Copia el token proporcionado

2. **OpenAI API Key**:
   - Ve a https://platform.openai.com/api-keys
   - Crea una nueva API key
   - ⚠️ **Importante**: Asegúrate de tener créditos en tu cuenta

3. **Tu Telegram User ID** (opcional):
   - Habla con @userinfobot para obtener tu ID
   - Úsalo como ADMIN_USER_ID para funciones administrativas

## 📁 Estructura del Proyecto

```
nelida-assistant/
├── src/
│   ├── bot/           # Bot de Telegram
│   ├── ai/            # Cliente OpenAI + Function Calling
│   ├── functions/     # Funciones específicas
│   ├── database/      # Base de datos
│   └── utils/         # Utilidades
├── data/              # Base de datos SQLite
├── logs/              # Archivos de log
├── main.py           # Punto de entrada
└── requirements.txt   # Dependencias
```

## 🎯 Uso

1. **Iniciar conversación**: Envía `/start` a tu bot
2. **Pedir ayuda**: Usa `/help` para ver comandos
3. **Hablar naturalmente**: 
   - "Recuérdame llamar al médico mañana a las 10"
   - "Busca información sobre Python"
   - "¿Qué tiempo hace hoy?"

## 🔍 Ejemplos de Uso

```
Usuario: "Hola Nelida"
Nelida: "¡Hola! Soy Nelida, tu secretaria personal. ¿En qué puedo ayudarte hoy?"

Usuario: "¿Cuál es el estado del sistema?"
Nelida: "Todos los sistemas están operando normalmente. Tengo 2 funciones disponibles y estoy lista para trabajar. ¿Necesitas algo más?"
```

## 🐛 Solución de Problemas

### Error: "Faltan variables de entorno requeridas"
- Verifica que `.env` tenga `TELEGRAM_BOT_TOKEN` y `OPENAI_API_KEY`
- Asegúrate de que los tokens sean válidos

### Error: "Error configurando bot"
- Verifica tu token de Telegram con @BotFather
- Comprueba tu conexión a internet

### Error: "Error procesando mensaje con OpenAI"
- Verifica tu API key de OpenAI
- Asegúrate de tener créditos disponibles
- Revisa los logs en `logs/nelida.log`

## 📈 Desarrollo

### Agregar Nuevas Funciones

1. **Crear función en `src/functions/`**:
   ```python
   from ..ai.function_registry import function_registry
   
   @function_registry.register("mi_funcion", {
       "type": "function",
       "function": {
           "name": "mi_funcion",
           "description": "Descripción de la función",
           "parameters": {...}
       }
   })
   async def mi_funcion(parametro: str):
       return "Resultado"
   ```

2. **Importar en `main.py`** para registrar automáticamente

### Logs y Debugging

- Los logs se guardan en `logs/nelida.log`
- Nivel de log configurable en `.env` (DEBUG, INFO, WARNING, ERROR)
- Rotación automática de logs (10MB, 7 días)

## 🚧 Roadmap

- ✅ **Fase 1**: Bot básico + OpenAI function calling
- ⏳ **Fase 2**: Recordatorios + búsquedas web
- 📅 **Fase 3**: Google Calendar + emails
- 🎭 **Fase 4**: Personalidad completa de Nelida
- 🐳 **Fase 5**: Dockerización y deployment

Ver [roadmap.md](roadmap.md) para detalles completos.

## 📄 Licencia

Este proyecto es de uso personal. Desarrollado con ❤️ para hacer la vida más fácil.

---

**¿Problemas?** Abre un issue o revisa los logs. Nelida siempre está lista para ayudar 🚬