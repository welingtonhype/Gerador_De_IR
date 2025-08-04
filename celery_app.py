"""
Celery App para processamento assíncrono
"""

from celery import Celery
import os
from config import get_config

config = get_config()

# Configurar Celery
celery_app = Celery(
    'gerador_ir',
    broker=config['CELERY']['BROKER_URL'],
    backend=config['CELERY']['RESULT_BACKEND']
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer=config['CELERY']['TASK_SERIALIZER'],
    accept_content=config['CELERY']['ACCEPT_CONTENT'],
    result_serializer=config['CELERY']['RESULT_SERIALIZER'],
    timezone=config['CELERY']['TIMEZONE'],
    enable_utc=config['CELERY']['ENABLE_UTC'],
    task_track_started=config['CELERY']['TASK_TRACK_STARTED'],
    task_time_limit=config['CELERY']['TASK_TIME_LIMIT'],
    worker_max_tasks_per_child=config['CELERY']['WORKER_MAX_TASKS_PER_CHILD']
)

# Importar tasks
celery_app.autodiscover_tasks(['tasks']) 