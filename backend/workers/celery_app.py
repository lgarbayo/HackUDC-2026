"""
workers/celery_app.py — EL CAMARERO Y LA COCINA (Celery).
--------------------------------------------------------
¿Alguna vez has pedido comida en un restaurante? El camarero anota 
tu pedido rápido para atender a otro cliente, mientras la cocina (el Worker) 
prepara tu plato con calma.

¡Celery es ese sistema de gestión!
1. FastAPI (El Camarero): Recibe tu archivo y dice: "¡Pedido recibido!".
2. Redis (La Comanda): Es la nota donde se apunta: "Hay que procesar 'doc.pdf'".
3. Celery Worker (La Cocina): Coge la nota de Redis y se pone a trabajar 
   en el archivo sin bloquear al camarero.

Esto permite que la web de MeigaSearch sea súper rápida aunque subas 
un manual de 500 páginas.
"""

from celery import Celery

from core.config import settings

# Instancia principal de Celery.
# "meiga_worker" identifica la aplicación dentro del ecosistema de workers.
celery_app = Celery(
    "meiga_worker",
    broker=settings.REDIS_URL,          # Cola donde se depositan las tareas.
    backend=settings.REDIS_URL,         # Donde se guardan los resultados/errores.
    include=["workers.tasks"],          # Registro de módulos que contienen @task.
)

# Afinamiento de la configuración para producción.
celery_app.conf.update(
    # Seguridad y formato de datos
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Localización temporal para logs y scheduling corregido
    timezone="Europe/Madrid",
    enable_utc=True,

    # Estrategia de Fiabilidad:
    # task_acks_late: El worker confirma la tarea SOLO después de terminarla. 
    # Si el worker muere a mitad, la tarea vuelve a la cola (evita pérdida de datos).
    task_acks_late=True,
    
    # worker_prefetch_multiplier: Solo reserva 1 tarea por worker simultáneamente. 
    # Crítico cuando las tareas consumen mucha RAM (como la extracción de PDFs grandes).
    worker_prefetch_multiplier=1,

    # Ciclo de vida de los resultados (1 hora) para no saturar Redis.
    result_expires=3600,

    # Compatibilidad con versiones modernas de Celery
    broker_connection_retry_on_startup=True,
)
