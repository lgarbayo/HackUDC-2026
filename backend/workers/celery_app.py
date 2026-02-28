"""
workers/celery_app.py — Configuración de Celery.

Celery se conecta a Redis como broker (cola de mensajes) y backend (resultados).
Este módulo crea la instancia de Celery que se importa en tasks.py y se referencia
en docker-compose para lanzar el worker.

Ejecución del worker:
    celery -A workers.celery_app worker --loglevel=info
"""

from celery import Celery

from core.config import settings

# Crear instancia de Celery
# El primer argumento es el nombre del módulo (para auto-discovery de tareas)
celery_app = Celery(
    "meiga_worker",
    broker=settings.REDIS_URL,          # Cola de mensajes
    backend=settings.REDIS_URL,         # Almacén de resultados
    include=["workers.tasks"],          # Módulos con tareas a descubrir
)

# Configuración adicional
celery_app.conf.update(
    # Serialización
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="Europe/Madrid",
    enable_utc=True,

    # Reintentos: si una tarea falla, reintenta hasta 3 veces con backoff
    task_acks_late=True,                # Acknowledges DESPUÉS de ejecutar (más seguro)
    worker_prefetch_multiplier=1,       # Un task a la vez por worker (controla memoria)

    # Resultados expiran en 1 hora
    result_expires=3600,

    # Evitar CPendingDeprecationWarning en Celery 6.0+
    broker_connection_retry_on_startup=True,
)
