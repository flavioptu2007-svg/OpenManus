"""Tarefas assíncronas com Celery."""
from app.tasks.image_tasks import make_celery, register_tasks, _notify_webhook

__all__ = ["make_celery", "register_tasks", "_notify_webhook"]
