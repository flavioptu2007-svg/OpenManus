"""Tarefas assíncronas com Celery."""

from app.tasks.image_tasks import _notify_webhook, make_celery, register_tasks


__all__ = ["make_celery", "register_tasks", "_notify_webhook"]
