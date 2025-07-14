# Roadmap - Nelida Assistant 🤖

## Visión General
Bot de Telegram con IA que funciona como secretaria personal, capaz de ejecutar tareas del sistema y mantener conversaciones inteligentes.

## Estado Actual: ✅ INICIO - Infraestructura Base

---

## 📋 Fases de Desarrollo

### ✅ **Fase 1: Infraestructura Base** (COMPLETADA)
**Objetivo**: Crear la base técnica del proyecto

#### ✅ Completado:
- [x] Estructura de carpetas del proyecto
- [x] requirements.txt con todas las dependencias
- [x] Archivo .env.example para configuración
- [x] Bot básico de Telegram funcionando
- [x] Integración OpenAI + Function Calling
- [x] Sistema de logging estructurado
- [x] Personalidad de Nélida configurada

---

### ✅ **Fase 2: Sistema de Recordatorios** (COMPLETADA)
**Objetivo**: Secretaria que maneja recordatorios con lenguaje natural

#### ✅ Completado:
- [x] **Base de datos SQLite**
  - [x] Tabla recordatorios con todos los campos
  - [x] Funciones CRUD completas
  - [x] Índices para performance
  
- [x] **Comandos manuales funcionando**
  - [x] crear:, listar, pendientes, completar
  - [x] Parser básico de fechas
  
- [x] **🚀 LENGUAJE NATURAL CON IA**
  - [x] Function calling con OpenAI
  - [x] Parser inteligente de fechas (mañana, viernes, próxima semana)
  - [x] Interpretar intenciones naturales
  - [x] Respuestas con personalidad de Nélida

---

### ✅ **Fase 3: Búsquedas en Internet** (COMPLETADA)

#### ✅ **Búsquedas en Internet** (COMPLETADO)
- [x] **Google Search API + DuckDuckGo fallback**
  - [x] "Nélida, buscame información sobre Python"
  - [x] "¿Qué tiempo va a hacer mañana?"
  - [x] "Investigame sobre cursos de programación"
- [x] **Integración con Function Calling**
- [x] **Respuestas con contexto argentino por defecto**
- [x] **Lectura de contenido de páginas web**
- [x] **Validación de fechas y tiempo**

---

### ✅ **Fase 4: RSS Feeds Noticias Argentinas** (COMPLETADA)

#### ✅ **Sistema RSS** (COMPLETADO)
- [x] **Feeds de medios argentinos**
  - [x] Clarín, La Nación, Infobae, Perfil (sin Página 12)
  - [x] Noticias reales de "hoy" (no resultados antiguos)
  - [x] Function calling con "obtener_noticias_hoy"
- [x] **Integración completa con Nélida**
- [x] **Parsing inteligente con timezone argentino**

#### 🔄 **Pendientes RSS (para el futuro)**
- [ ] Mejorar filtros por categoría (política, economía, deportes)
- [ ] Optimizar feeds y agregar más fuentes argentinas

---

### ✅ **Fase 5: Sistema de Tareas Inteligente** (COMPLETADA)

#### ✅ **Sistema de Tareas con IA** (COMPLETADO)
- [x] **Creación de tareas con lenguaje natural**
  - [x] "Tengo que llamar al médico y comprar leche"
  - [x] Detección automática de múltiples tareas
  - [x] Categorización inteligente (trabajo, casa, salud, estudios)
  - [x] Detección de prioridad (urgente, importante, normal)
- [x] **Gestión completa de tareas**
  - [x] Listar tareas pendientes/completadas
  - [x] Completar múltiples tareas con texto libre
  - [x] Búsqueda de tareas por contenido
  - [x] Function calling completo con OpenAI
- [x] **Base de datos optimizada**
  - [x] Tabla tareas con categorías y prioridades
  - [x] Índices para performance

---

### ✅ **Fase 6: Deploy con Docker + Notificaciones Automáticas** (COMPLETADA ✨)

#### ✅ **Containerización Completa** (COMPLETADO)
- [x] **Dockerfile optimizado**
  - [x] Multi-stage build con Python 3.11
  - [x] Usuario no-root para seguridad
  - [x] Timezone Argentina configurado
  - [x] Healthcheck automático
- [x] **Docker Compose orquestación**
  - [x] Variables de entorno desde .env
  - [x] Volumes persistentes para BD y logs
  - [x] Configuración de memoria y CPU
  - [x] Auto-restart en fallos
- [x] **Scripts de deploy automatizados**
  - [x] `deploy.sh` con comandos (start/stop/restart/logs/status)
  - [x] Setup automático con corrección de permisos
  - [x] Validación de variables de entorno
  - [x] Healthcheck y monitoreo

#### ✅ **Sistema de Notificaciones Programadas** (COMPLETADO)
- [x] **Scheduler integrado**
  - [x] Notificaciones automáticas 10:20-10:40 AM
  - [x] Resumen inteligente de tareas pendientes
  - [x] Organización por prioridad y categoría
  - [x] Ejecuta en hilo separado sin bloquear el bot
- [x] **Configuración flexible**
  - [x] Horarios configurables via .env
  - [x] Timezone argentino
  - [x] Comando `/test_notification` para pruebas
- [x] **Integración completa**
  - [x] Scheduler se inicia automáticamente con el bot
  - [x] Logging de notificaciones enviadas
  - [x] Manejo de errores robusto

#### ✅ **Documentación de Deploy** (COMPLETADO)
- [x] **DEPLOY.md completo**
  - [x] Guía paso a paso para servidor
  - [x] Configuración de variables de entorno
  - [x] Comandos de gestión y troubleshooting
  - [x] Ejemplos de uso y verificación
- [x] **Archivos de configuración**
  - [x] `.env.example` actualizado con todas las variables
  - [x] `docker-entrypoint.sh` con validaciones
  - [x] Scripts automatizados de setup

---

### 🔥 **Fase 7: Próximas Funcionalidades** (EN PLANIFICACIÓN)

#### 🎯 **Opción A: Sistema de Emails** (RECOMENDADO - 2-3 días)
- [ ] **Lectura de emails (IMAP)**
  - [ ] "Nélida, ¿tengo algo importante en el mail?"
  - [ ] Análisis inteligente de importancia/urgencia
  - [ ] Detección de reuniones, fechas límite, facturas
  - [ ] Resúmenes automáticos de emails largos
- [ ] **Envío de emails**
  - [ ] "Nélida, mandá email confirmando reunión"
  - [ ] Templates inteligentes según contexto

#### 🌐 **Opción B: RSS Feeds para Noticias** (1 día)
- [ ] **Feeds argentinos actualizados**
  - [ ] Clarín, La Nación, Página 12, Infobae RSS
  - [ ] Noticias realmente de "hoy"
  - [ ] Categorización automática (política, economía, etc.)
- [ ] **Función de noticias mejorada**

#### 🔔 **Opción C: Notificaciones Automáticas** (1-2 días)
- [ ] **Scheduler de recordatorios**
  - [ ] Revisa recordatorios cada X minutos
  - [ ] Envío automático de mensajes
  - [ ] "¡Ey pibe! No te olvides de llamar al médico"
- [ ] **Sistema de alertas inteligentes**

#### 📅 **Opción D: Google Calendar Integration** (2-3 días)
- [ ] **OAuth2 con Google APIs**
- [ ] **Sincronización bidireccional**
  - [ ] "Nélida, agregá reunión al calendario para el jueves"
  - [ ] "¿Qué tengo en mi agenda hoy?"
- [ ] **Gestión completa de eventos**

#### 🛫 **Opción E: Skyscanner/Viajes** (2-3 días)
- [ ] **Búsqueda de vuelos**
  - [ ] "Nélida, buscame vuelos a Madrid desde Buenos Aires"
  - [ ] Integración con Skyscanner API o scraping
  - [ ] Comparación de precios y fechas
  - [ ] Sugerencias de mejores opciones
- [ ] **Hoteles y alojamiento**
  - [ ] Búsqueda de hoteles en destino
  - [ ] Comparación de precios

#### 📝 **Opción F: Notas/Tareas Inteligentes** (1-2 días)
- [ ] **Sistema de notas con IA**
  - [ ] "Nélida, guardá esta información sobre X"
  - [ ] "¿Qué anotaste sobre el proyecto Y?"
- [ ] **Categorización automática**
- [ ] **Búsqueda semántica en notas**

---

### 🎭 **Fase 4: Funcionalidades Avanzadas** (FUTURO)

#### 🌐 **Integraciones Externas**
- [ ] **APIs del Clima**
- [ ] **Conversión de monedas**
- [ ] **Noticias y feeds RSS**
- [ ] **Traducción automática**

#### 🧠 **IA Avanzada**
- [ ] **Memoria a largo plazo**
- [ ] **Aprendizaje de preferencias del usuario**
- [ ] **Análisis de sentimientos**
- [ ] **Generación de reportes automáticos**

---

### 🐳 **Fase 5: Deployment y Producción** (FUTURO)

#### **Containerización**
- [ ] **Dockerfile optimizado**
- [ ] **docker-compose.yml completo**
- [ ] **Variables de entorno seguras**

#### **Automatización y Monitoreo**
- [ ] **Scripts de inicio automático**
- [ ] **Reinicio automático en fallos**
- [ ] **Monitoreo de salud del bot**
- [ ] **Métricas de uso y performance**
- [ ] **Backups automáticos de BD**

#### **Seguridad**
- [ ] **Encriptación de datos sensibles**
- [ ] **Rate limiting**
- [ ] **Validación de entrada robusta**

---

## 🏗️ Arquitectura Técnica

### Componentes Principales:
1. **Telegram Bot** → Interfaz de usuario
2. **OpenAI Client** → Procesamiento de IA con Function Calling
3. **Function Registry** → Registro de funciones disponibles
4. **Database Layer** → Almacenamiento persistente
5. **External APIs** → Google Calendar, Email, etc.

### Flujo de Trabajo:
```
Usuario → Telegram → Message Handler → OpenAI + Functions → Ejecutor → Respuesta
```

---

## 📁 Estructura del Proyecto

```
nelida-assistant/
├── src/
│   ├── bot/                # Bot de Telegram
│   ├── ai/                 # Cliente OpenAI + Function Calling  
│   ├── functions/          # Funciones específicas (email, calendario, etc.)
│   ├── database/           # Modelos y conexión DB
│   └── utils/              # Utilidades (logging, config)
├── data/                   # Base de datos SQLite
├── logs/                   # Archivos de log
├── requirements.txt
├── .env.example
└── main.py
```

---

## 🎯 Próximos Pasos

1. **Inmediato**: Completar bot básico de Telegram
2. **Esta semana**: Function calling con OpenAI funcionando
3. **Próxima semana**: Primeras funciones (recordatorios + búsquedas)

---

## 📝 Notas de Desarrollo

### Function Calling con OpenAI:
- Cada funcionalidad será una función Python separada
- OpenAI puede llamar estas funciones y esperar resultados
- Mantenemos conversaciones persistentes para continuidad

### Funciones Planificadas:
- `enviar_email()` - Envío de correos
- `buscar_google()` - Búsquedas web
- `crear_recordatorio()` - Gestión de recordatorios
- `consultar_calendario()` - Google Calendar
- `guardar_nota()` - Almacenamiento de información
- `consultar_clima()` - Información meteorológica

---

## 📧 **Notas Técnicas: Implementación de Emails**

### **Lectura de Emails (IMAP)**
- **Gmail**: Usar OAuth2 + IMAP (imap.gmail.com:993)
- **Outlook**: IMAP (outlook.office365.com:993) 
- **Otros**: Configuración IMAP estándar
- **Bibliotecas**: `imaplib` (nativo) o `imapclient` (más fácil)

### **Análisis Inteligente con IA**
- **Clasificación**: Urgente/Normal/Spam usando OpenAI
- **Extracción**: Fechas, contactos, tareas usando NER
- **Resumen**: Condensar emails largos automáticamente
- **Contexto**: Relacionar emails con recordatorios existentes

### **Configuración de Seguridad**
- **App Passwords**: Para Gmail (no usar contraseña principal)
- **OAuth2**: Método recomendado para producción
- **Encriptación**: Credenciales encriptadas en .env
- **Rate Limiting**: No hacer spam a los servidores de email

### **Function Calling para Emails**
```python
# Ejemplos de funciones:
- leer_emails_recientes(cantidad=10, solo_no_leidos=True)
- analizar_importancia_email(email_id)
- buscar_emails(query="reunión", desde="2024-01-01") 
- crear_resumen_emails(fecha="hoy")
```

---

---

## 📊 **Estado Actual del Proyecto**

**✅ COMPLETADO:**
- ✅ **Infraestructura base** (Telegram bot + OpenAI + Function Calling)
- ✅ **Sistema de recordatorios** (con IA y lenguaje natural)  
- ✅ **Búsquedas en internet** (Google API + contexto argentino)
- ✅ **RSS feeds noticias** (Clarín, La Nación, Infobae, Perfil)
- ✅ **Sistema de tareas inteligente** (creación, gestión y completado con IA)
- ✅ **Deploy con Docker** (containerización completa + scripts automatizados)
- ✅ **Notificaciones automáticas** (scheduler 10:20-10:40 AM con resumen de tareas)
- ✅ **Validación de fechas/tiempo** (timezone argentino)

**🎯 PRÓXIMO EN LA LISTA:**
- 📧 **Sistema de Emails** (lectura + envío inteligente)
- 📅 **Google Calendar** (sincronización bidireccional)
- 🛫 **Skyscanner/Viajes** (búsqueda de vuelos)
- 🧠 **Memoria a largo plazo** (recordar conversaciones y preferencias)

---

## 🎉 **HITO IMPORTANTE ALCANZADO** (14/07/2025)

**✨ NELIDA ASSISTANT YA ESTÁ 100% OPERATIVA PARA PRODUCCIÓN ✨**

### **🚀 Lo que funciona HOY:**
1. **Secretaria completa** con IA para tareas, recordatorios, búsquedas
2. **Deploy automatizado** con Docker en servidor 
3. **Notificaciones matutinas** automáticas de tareas pendientes
4. **Gestión inteligente** de múltiples tareas con lenguaje natural
5. **Búsquedas web** con contexto argentino
6. **Noticias actualizadas** de medios argentinos
7. **Sistema robusto** con auto-restart, logs y healthcheck

### **📱 Comandos disponibles:**
- Cualquier conversación natural con Nélida
- `/start` - Iniciar bot
- `/status` - Ver estado del sistema  
- `/test_notification` - Probar notificaciones (solo admin)
- `/help` - Ver todas las funcionalidades

### **⏰ Funcionalidad estrella:**
**Notificaciones automáticas entre 10:20-10:40 AM** con resumen completo de:
- 🔴 Tareas urgentes
- 🟡 Tareas importantes  
- 🟢 Tareas para cuando puedas
- 📁 Resumen por categorías (trabajo, casa, salud, estudios)

**✅ LISTO PARA USAR MAÑANA EN EL TRABAJO** 💼

---

*Última actualización: 14/07/2025 - Deploy en producción completado*