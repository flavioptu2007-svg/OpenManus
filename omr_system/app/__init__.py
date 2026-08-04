"""Application Factory."""

import logging
import os

from flask import Flask

from app.config import config_by_name
from app.extensions import cache, db, jwt, limiter, migrate
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
    from app.api.v1 import api_v1_bp
    from app.auth.routes import auth_bp
    from app.routes.exam_routes import exam_bp

    app.register_blueprint(exam_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_v1_bp)

    @app.route("/")
    def index():
        return {
            "app": "Sistema de Gabaritos",
            "version": "3.0.0",
            "auth": "/api/v1/auth/login",
        }

    with app.app_context():
        from app.models.exam import Questao, seed_questoes
        from app.models.user import AuditLog, User

        db.create_all()
        _ensure_questao_columns()
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


def _ensure_questao_columns() -> None:
    """Migração aditiva idempotente: adiciona materia/serie à tabela questoes.

    db.create_all() não altera tabelas existentes — o dev_app.db versionado
    precisa das colunas novas sem perder dados.
    """
    from sqlalchemy import inspect as sa_inspect
    from sqlalchemy import text

    insp = sa_inspect(db.engine)
    cols = {c["name"] for c in insp.get_columns("questoes")}
    for col, ddl in (("materia", "VARCHAR(60)"), ("serie", "VARCHAR(30)")):
        if col not in cols:
            db.session.execute(text(f"ALTER TABLE questoes ADD COLUMN {col} {ddl}"))
            logger.info(f"Coluna 'questoes.{col}' adicionada.")
    db.session.commit()
