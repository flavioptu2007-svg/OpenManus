"""Endpoints de autenticação JWT."""
import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from marshmallow import ValidationError as MarshmallowError

from app.extensions import db, limiter
from app.models.user import User, AuditLog
from app.schemas.exam_schema import login_schema

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

# Blocklist simples em memória (em produção use Redis)
BLOCKLIST: set = set()


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5/minute")
def register():
    """
    Registra novo usuário.
    Body: { username, email, password }
    """
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "username, email e password são obrigatórios."}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username já existe."}), 409
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email já cadastrado."}), 409

    user = User(username=data["username"], email=data["email"])
    user.password = data["password"]
    db.session.add(user)
    db.session.commit()

    logger.info(f"Usuário criado: {user.username}")
    return jsonify(user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    """
    Autentica usuário e retorna tokens JWT.
    Body: { username, password }
    """
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except MarshmallowError as e:
        return jsonify({"error": e.messages}), 400

    user = User.query.filter_by(username=data["username"], is_active=True).first()
    if not user or not user.verify_password(data["password"]):
        return jsonify({"error": "Credenciais inválidas."}), 401

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    log = AuditLog(
        user_id=user.id, action="LOGIN", entity="User",
        entity_id=user.id, ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"access_token": access, "refresh_token": refresh}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Gera novo access token via refresh token."""
    identity = get_jwt_identity()
    token = create_access_token(identity=identity)
    return jsonify({"access_token": token}), 200


@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """Invalida o token atual (adiciona à blocklist)."""
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    return jsonify({"message": "Token invalidado com sucesso."}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retorna dados do usuário autenticado."""
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404
    return jsonify(user.to_dict()), 200
