"""Endpoints da API de Provas e Questões — com JWT, Marshmallow e Cache."""

import logging
from datetime import datetime

from flask import Blueprint, current_app, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError as MarshmallowError

from app.api.v1.security import api_auth
from app.exceptions import NotFoundError, ValidationError
from app.extensions import cache, db, limiter
from app.models.user import AuditLog
from app.repositories.exam_repo import prova_repo, questao_repo
from app.schemas.exam_schema import (
    pagination_schema,
    prova_create_schema,
    questao_schema,
)
from app.services.exam_service import ExamService
from app.services.image_service import ImageService
from app.utils.export import export_questoes_csv, export_to_csv, export_to_json


logger = logging.getLogger(__name__)
exam_bp = Blueprint("exam", __name__, url_prefix="/api/v1")


# ── helpers ──────────────────────────────────────────────────────────────── #


def _audit(action: str, entity: str, entity_id: int = None, details: str = None):
    uid = None
    try:
        raw = get_jwt_identity()
        uid = int(raw) if raw else None
    except Exception:
        pass
    log = AuditLog(
        user_id=uid,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()


def _pagination():
    """Suporta page/per_page (legado) e limit/offset (API v1) em paralelo."""
    args = request.args.to_dict()
    out = {}
    try:
        out.update(pagination_schema.load(args))
    except MarshmallowError as e:
        raise ValidationError(str(e.messages))
    if "limit" in args or "offset" in args:
        try:
            out["limit"] = int(args.get("limit", 50))
            out["offset"] = max(int(args.get("offset", 0)), 0)
        except ValueError:
            raise ValidationError("limit e offset devem ser inteiros.")
    return out


# ── health ───────────────────────────────────────────────────────────────── #


@exam_bp.route("/health")
def health():
    return jsonify({"status": "ok", "ts": datetime.utcnow().isoformat()}), 200


# ── upload (assíncrono via Celery) ───────────────────────────────────────── #


@exam_bp.route("/upload", methods=["POST"])
@api_auth
@limiter.limit("20/minute")
def upload_image():
    """
    Upload de imagem de gabarito — processamento assíncrono via Celery.
    Retorna task_id para consulta de status.
    """
    if "image" not in request.files:
        raise ValidationError("O campo 'image' é obrigatório.")

    try:
        data = prova_create_schema.load(request.form.to_dict())
    except MarshmallowError as e:
        raise ValidationError(str(e.messages))

    svc = ImageService(current_app.config["UPLOAD_FOLDER"])
    saved = svc.save_only(request.files["image"])
    prova = ExamService.create_pending(
        webhook_url=data.get("webhook_url"),
        nome=data.get("nome"),
    )

    # Processamento síncrono (Celery não configurado nesta versão)
    result = svc.process_image(saved["filepath"])
    ExamService.finalize_from_image(
        prova, result["qr_data"], result["marked_answers_count"]
    )
    _audit("UPLOAD_SYNC", "Prova", prova.id)
    return jsonify(prova.to_dict()), 200


@exam_bp.route("/upload/<int:prova_id>/status")
@api_auth
def upload_status(prova_id: int):
    """Consulta o status de processamento de uma prova."""
    prova = prova_repo.get_by_id(prova_id)
    if not prova:
        raise NotFoundError(f"Prova {prova_id} não encontrada.")
    return (
        jsonify(
            {"prova_id": prova.id, "status": prova.status, "task_id": prova.task_id}
        ),
        200,
    )


# ── upload bulk ──────────────────────────────────────────────────────────── #


@exam_bp.route("/upload/bulk", methods=["POST"])
@api_auth
@limiter.limit("5/minute")
def upload_bulk():
    """
    Upload de múltiplas imagens de gabarito.
    Aceita até 10 arquivos no campo 'images[]'.
    """
    files = request.files.getlist("images[]")
    if not files:
        raise ValidationError("Envie ao menos uma imagem no campo 'images[]'.")
    if len(files) > 10:
        raise ValidationError("Máximo de 10 imagens por requisição.")

    svc = ImageService(current_app.config["UPLOAD_FOLDER"])
    results = []
    for f in files:
        try:
            saved = svc.save_only(f)
            result = svc.process_image(saved["filepath"])
            prova = ExamService.create_from_image(
                result["qr_data"], result["marked_answers_count"]
            )
            results.append({"file": f.filename, "prova_id": prova.id, "status": "done"})
        except Exception as e:
            results.append({"file": f.filename, "error": str(e)})

    return jsonify({"results": results, "total": len(results)}), 207


# ── provas ───────────────────────────────────────────────────────────────── #


@exam_bp.route("/provas", methods=["POST"])
@api_auth
@limiter.limit("20/minute")
def criar_prova():
    """Cria prova associando questões (por IDs informados ou não atribuídas)."""
    try:
        data = prova_create_schema.load(request.get_json(silent=True) or {})
    except MarshmallowError as e:
        raise ValidationError(str(e.messages))

    prova = ExamService.create_with_questions(
        nome=data.get("nome"), question_ids=data.get("question_ids")
    )
    _audit("CREATE_PROVA", "Prova", prova.id)
    cache.delete_memoized(listar_provas)
    return jsonify(prova.to_dict(include_questoes=True)), 201


@exam_bp.route("/provas", methods=["GET"])
@api_auth
@cache.cached(timeout=60, query_string=True)
def listar_provas():
    """Lista provas com paginação page/per_page ou limit/offset."""
    p = _pagination()
    return (
        jsonify(
            ExamService.list_paginated(
                p.get("page", 1), p.get("per_page", 10), p.get("limit"), p.get("offset")
            )
        ),
        200,
    )


@exam_bp.route("/provas/<int:prova_id>")
@api_auth
def obter_prova(prova_id: int):
    """Retorna detalhes de uma prova com questões."""
    prova = prova_repo.get_by_id(prova_id)
    if not prova:
        raise NotFoundError(f"Prova {prova_id} não encontrada.")
    return jsonify(prova.to_dict(include_questoes=True)), 200


@exam_bp.route("/provas/<int:prova_id>", methods=["DELETE"])
@api_auth
def deletar_prova(prova_id: int):
    """Soft-delete de uma prova."""
    prova = prova_repo.get_by_id(prova_id)
    if not prova:
        raise NotFoundError(f"Prova {prova_id} não encontrada.")
    prova_repo.delete(prova)
    _audit("DELETE_PROVA", "Prova", prova_id)
    cache.delete_memoized(listar_provas)
    return jsonify({"message": f"Prova {prova_id} removida."}), 200


# ── export ───────────────────────────────────────────────────────────────── #


@exam_bp.route("/provas/export")
@api_auth
def export_provas():
    """
    Exporta todas as provas.
    Query param: format=csv|json (padrão: json)
    """
    fmt = request.args.get("format", "json").lower()
    provas = prova_repo.get_all()

    if fmt == "csv":
        resp = make_response(export_to_csv(provas))
        resp.headers["Content-Type"] = "text/csv"
        resp.headers["Content-Disposition"] = "attachment; filename=provas.csv"
        return resp

    resp = make_response(export_to_json(provas))
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Disposition"] = "attachment; filename=provas.json"
    return resp


@exam_bp.route("/provas/<int:prova_id>/export")
@api_auth
def export_questoes(prova_id: int):
    """Exporta questões de uma prova em CSV."""
    prova = prova_repo.get_by_id(prova_id)
    if not prova:
        raise NotFoundError(f"Prova {prova_id} não encontrada.")
    resp = make_response(export_questoes_csv(prova))
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = (
        f"attachment; filename=questoes_prova_{prova_id}.csv"
    )
    return resp


# ── questões ─────────────────────────────────────────────────────────────── #


@exam_bp.route("/questoes", methods=["GET"])
@api_auth
@cache.cached(timeout=60, query_string=True)
def listar_questoes():
    """Lista questões com filtros (materia/serie/dificuldade) e paginação."""
    p = _pagination()
    return (
        jsonify(
            ExamService.list_questoes_paginated(
                p.get("page", 1),
                p.get("per_page", 10),
                p.get("limit"),
                p.get("offset"),
                request.args.get("materia"),
                request.args.get("serie"),
                request.args.get("dificuldade"),
            )
        ),
        200,
    )


@exam_bp.route("/questoes", methods=["POST"])
@api_auth
@limiter.limit("30/minute")
def criar_questao():
    """Cria nova questão com validação via Marshmallow."""
    try:
        data = questao_schema.load(request.get_json(silent=True) or {})
    except MarshmallowError as e:
        raise ValidationError(str(e.messages))

    q = ExamService.add_questao(
        data["texto"],
        data.get("habilidade"),
        data.get("dificuldade"),
        data.get("materia"),
        data.get("serie"),
    )
    _audit("CREATE_QUESTAO", "Questao", q.id)
    cache.delete_memoized(listar_questoes)
    return jsonify(q.to_dict()), 201


@exam_bp.route("/questoes/<int:q_id>", methods=["DELETE"])
@api_auth
def deletar_questao(q_id: int):
    """Soft-delete de uma questão."""
    q = questao_repo.get_by_id(q_id)
    if not q:
        raise NotFoundError(f"Questão {q_id} não encontrada.")
    questao_repo.delete(q)
    _audit("DELETE_QUESTAO", "Questao", q_id)
    return jsonify({"message": f"Questão {q_id} removida."}), 200
