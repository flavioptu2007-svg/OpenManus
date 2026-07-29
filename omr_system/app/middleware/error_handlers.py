"""Error handlers globais da aplicação."""
import logging

from flask import jsonify

from app.exceptions import ValidationError, NotFoundError, ImageProcessingError, StorageError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registra handlers de erro para toda a aplicação."""

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(ImageProcessingError)
    def handle_image_error(e):
        return jsonify({"error": str(e)}), 422

    @app.errorhandler(StorageError)
    def handle_storage_error(e):
        logger.error(f"Erro de armazenamento: {e}")
        return jsonify({"error": "Erro interno de armazenamento."}), 500

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Requisição inválida."}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Não autorizado."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Acesso negado."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método não permitido."}), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "Entidade não processável."}), 422

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"error": "Muitas requisições. Aguarde e tente novamente."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Erro interno: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor."}), 500

    logger.info("Error handlers registrados.")
