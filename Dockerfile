# Dockerfile para Nelida Assistant
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo temporal
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa final - imagen mínima
FROM python:3.11-slim

# Crear usuario no-root para seguridad
RUN groupadd -r nelida && useradd -r -g nelida nelida

# Instalar dependencias mínimas del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs && \
    chown -R nelida:nelida /app

# Copiar dependencias Python instaladas
COPY --from=builder /root/.local /home/nelida/.local

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=nelida:nelida . .

# Configurar PATH para dependencias de usuario
ENV PATH=/home/nelida/.local/bin:$PATH

# Cambiar a usuario no-root
USER nelida

# Configurar timezone
ENV TZ=America/Argentina/Buenos_Aires

# Exponer puerto (opcional, solo para debugging)
EXPOSE 8000

# Script de entrada
COPY docker-entrypoint.sh /docker-entrypoint.sh
USER root
RUN chmod +x /docker-entrypoint.sh
USER nelida

# Healthcheck para verificar que el bot esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('/app/logs/nelida.log') else 1)"

# Comando por defecto
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "main.py"]