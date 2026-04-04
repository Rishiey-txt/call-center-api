from celery import Celery
from src.config import settings

celery_app = Celery(
    "call_center",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.processing"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
)
