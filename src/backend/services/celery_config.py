from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

# Create single Celery instance
celery_app = Celery("gmail_tasks", broker=CELERY_BROKER_URL)

# Configuration
celery_app.conf.update(
    worker_pool="threads",
    worker_concurrency=8,
    task_acks_late=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    imports=["services.process_gmail", "services.process_telegram"],
    timezone="UTC",
    enable_utc=True,
    result_backend=CELERY_BROKER_URL.replace("amqp://", "rpc://"),
    task_default_retry_delay=60,
    task_max_retries=3,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=50,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['services'])
