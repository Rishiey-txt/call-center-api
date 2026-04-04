from src.tasks.celery_app import celery_app
from src.tasks import processing  # registers task decorators

if __name__ == "__main__":
    celery_app.start()
