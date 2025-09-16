import logging
import os

from celery import Celery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Выводим содержимое рабочей директории для отладки
logging.info("Contents of /app directory:")
try:
    for item in os.listdir('/app'):
        logging.info(f"- {item}")
except Exception as e:
    logging.error(f"Error listing directory /app: {e}")

REDIS_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
REDIS_RESULT_BACKEND_URL = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

celery = Celery(
    __name__,
    broker=REDIS_BROKER_URL,
    backend=REDIS_RESULT_BACKEND_URL
)

celery.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

celery.autodiscover_tasks(['tasks'])
