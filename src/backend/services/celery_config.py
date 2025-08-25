from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "message_tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND
)

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
    task_default_retry_delay=60,
    task_max_retries=3,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=50,
    task_routes={
        "services.process_gmail.*": {"queue": "gmail_process"},
        "services.process_telegram.*": {"queue": "telegram_process"},
    },
)

celery_app.autodiscover_tasks(["services"])
