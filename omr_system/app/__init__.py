"""Application Factory."""
import os
import logging

from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate, limiter, jwt, cache
from app.middleware.error_handlers import register_error_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Extensões
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)

    # JWT blocklist
    from app.auth.routes import BLOCKLIST

    @jwt.token_in_blocklist_loader
    def check_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    # Error handlers
    register_error_handlers(app)

    # Blueprints
    from app.routes.exam_routes import exam_bp
    from app.auth.routes import auth_bp
    app.register_blueprint(exam_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return {
            "app": "Sistema de Gabaritos",
            "version": "3.0.0",
            "auth": "/api/v1/auth/login",
        }

    with app.app_context():
        from app.models.exam import Questao, seed_questoes
        from app.models.user import User, AuditLog
        db.create_all()
        if Questao.query.count() == 0:
            seed_questoes()
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@escola.gov.br", is_admin=True)
            admin.password = "admin123"
            db.session.add(admin)
            db.session.commit()
            logger.info("Usuário admin criado.")

    logger.info(f"App v3.0.0 inicializado | config={config_name}")
    return app
