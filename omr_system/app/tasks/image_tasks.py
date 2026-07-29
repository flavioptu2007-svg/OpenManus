"""Tarefas Celery para processamento assíncrono de imagens."""
import logging

import requests
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def make_celery(app):
    """Cria instância do Celery integrada ao contexto Flask."""
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_tasks(celery):
    """Registra as tasks no Celery."""

    @celery.task(bind=True, max_retries=3, default_retry_delay=10)
    def process_image_task(self, prova_id: int, filepath: str):
        """
        Task assíncrona para processar imagem de gabarito.
        Atualiza o status da Prova no banco ao concluir.
        """
        from app.utils.omr import detect_answer_sheet
        from app.utils.qr_reader import decode_qr_codes
        from app.repositories.exam_repositories import prova_repo
        import cv2

        try:
            logger.info(f"Iniciando processamento | prova_id={prova_id}")
            prova_repo.update_status(prova_id, "processing")

            image = cv2.imread(filepath)
            qr_data = decode_qr_codes(image)
            result = detect_answer_sheet(image)

            prova = prova_repo.get_by_id(prova_id)
            if prova:
                prova.qr_code_info = ", ".join(qr_data)
                prova.marked_answers = result["marked_count"]
                prova.status = "done"
                from app.extensions import db
                db.session.commit()

                if prova.webhook_url:
                    _notify_webhook(prova.webhook_url, prova.to_dict())

            logger.info(f"Prova {prova_id} processada | marcações={result['marked_count']}")
            return result

        except Exception as exc:
            logger.error(f"Erro na task prova_id={prova_id}: {exc}")
            prova_repo.update_status(prova_id, "error")
            raise self.retry(exc=exc)

    return process_image_task


def _notify_webhook(url: str, payload: dict) -> None:
    """Envia notificação POST ao webhook configurado."""
    try:
        resp = requests.post(url, json=payload, timeout=10)
        logger.info(f"Webhook notificado | url={url} | status={resp.status_code}")
    except requests.RequestException as e:
        logger.warning(f"Falha ao notificar webhook {url}: {e}")
