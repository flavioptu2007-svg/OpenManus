"""Blueprint da API v1 — endpoints novos (gabaritos/processar e resultados).

Características:
- Paginação limit/offset com total, has_more e next_offset.
- Erros em formato estruturado ``{"error": {"code", "message", "suggestion"}}``.
- Autenticação X-API-Key ou JWT (ver app.api.v1.security).
- Validação de upload (tipo e tamanho) antes do OpenCV.
"""

import base64
import io
import logging
import os

from flask import Blueprint, current_app, jsonify, request
from werkzeug.datastructures import FileStorage

from app.api.v1.security import api_auth
from app.exceptions import ImageProcessingError, NotFoundError, ValidationError
from app.extensions import db, limiter
from app.models.prova import FolhaResposta
from app.models.user import AuditLog
from app.repositories.exam_repo import prova_repo
from app.repositories.folha_repository import FolhaRepository
from app.services.image_service import ImageService
from app.utils.validators import MAGIC_BYTES, MAX_FILE_SIZE, validate_image_file


logger = logging.getLogger(__name__)

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# ── helpers ──────────────────────────────────────────────────────────────── #


def _erro(code: str, message: str, suggestion: str, status: int = 400):
    return (
        jsonify(
            {"error": {"code": code, "message": message, "suggestion": suggestion}}
        ),
        status,
    )


def _parse_prova_id(valor):
    """Converte prova_id (form/JSON) com validação — nunca 500 por ValueError."""
    if valor is None or valor == "":
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValidationError("prova_id deve ser um inteiro.")


def _audit_v1(action: str, entity: str, entity_id: int = None, details: str = None):
    """Auditoria para chamadas autenticadas via API key (user_id = None)."""
    log = AuditLog(
        user_id=None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()


def _paginar(query, limit: int, offset: int, chave: str) -> dict:
    total = query.count()
    itens = query.order_by(FolhaResposta.id).offset(offset).limit(limit).all()
    next_off = offset + len(itens) if offset + len(itens) < total else None
    return {
        chave: [i.to_dict() for i in itens],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(itens) < total,
        "next_offset": next_off,
    }


# ── error handlers estruturados (escopo do blueprint) ────────────────────── #


@api_v1_bp.errorhandler(ValidationError)
def _handle_validation(e):
    return _erro(
        "VALIDATION_ERROR",
        str(e),
        "Revise os parâmetros enviados e tente novamente.",
        400,
    )


@api_v1_bp.errorhandler(NotFoundError)
def _handle_not_found(e):
    return _erro(
        "NOT_FOUND",
        str(e),
        "Confira o ID informado — use o endpoint de listagem para IDs válidos.",
        404,
    )


@api_v1_bp.errorhandler(ImageProcessingError)
def _handle_image(e):
    return _erro(
        "IMAGE_PROCESSING_ERROR",
        str(e),
        "Envie uma imagem nítida de gabarito em JPEG/PNG.",
        422,
    )


@api_v1_bp.errorhandler(404)
def _handle_404(e):
    return _erro(
        "NOT_FOUND", "Recurso não encontrado.", "Verifique a URL do endpoint.", 404
    )


@api_v1_bp.errorhandler(405)
def _handle_405(e):
    return _erro(
        "METHOD_NOT_ALLOWED",
        "Método não permitido.",
        "Confira o método HTTP usado na chamada.",
        405,
    )


# ── rotas ────────────────────────────────────────────────────────────────── #


@api_v1_bp.route("/gabaritos/processar", methods=["POST"])
@api_auth
@limiter.limit("20/minute")
def processar_gabarito():
    """Recebe imagem (multipart 'image' ou JSON 'image_base64') e retorna a
    leitura estruturada (QR + bolhas). Opcional: 'prova_id' persiste o resultado.

    Body (JSON): { "image_base64": "...", "filename": "gabarito.png", "prova_id": 1 }
    Form (multipart): image=<arquivo>, prova_id=<opcional>
    """
    payload = request.get_json(silent=True)
    arquivo = None
    prova_id = None

    if payload and payload.get("image_base64"):
        b64 = payload["image_base64"]
        if b64.startswith("data:"):
            b64 = b64.split(",", 1)[1]
        try:
            raw = base64.b64decode(b64, validate=True)
        except Exception:
            raise ValidationError("image_base64 inválido — não é base64 válido.")
        if not raw:
            raise ValidationError("image_base64 está vazio.")
        if len(raw) > MAX_FILE_SIZE:
            raise ValidationError(
                f"Imagem excede o limite de {MAX_FILE_SIZE // 1024 // 1024} MB."
            )
        if not any(raw.startswith(m) for m in MAGIC_BYTES):
            raise ValidationError(
                "Tipo de arquivo não reconhecido. Apenas JPEG e PNG são aceitos."
            )
        filename = payload.get("filename") or "gabarito_base64.png"
        arquivo = FileStorage(stream=io.BytesIO(raw), filename=filename)
        prova_id = _parse_prova_id(payload.get("prova_id"))
    elif request.files.get("image"):
        arquivo = request.files["image"]
        prova_id = _parse_prova_id(
            request.form.get("prova_id") or request.args.get("prova_id")
        )
    else:
        raise ValidationError(
            "Envie a imagem no campo 'image' (multipart) ou 'image_base64' (JSON)."
        )

    validate_image_file(arquivo)

    svc = ImageService(current_app.config["UPLOAD_FOLDER"])
    saved = svc.save_only(arquivo)
    result = svc.process_image(saved["filepath"])

    resposta = {
        "qr_data": result["qr_data"],
        "marked_answers_count": result["marked_answers_count"],
        "total_bubbles": result["total_bubbles"],
        "confidence": result["confidence"],
        "image_file": saved["filename"],
    }

    if prova_id:
        prova = prova_repo.get_by_id(prova_id)
        if not prova:
            os.remove(saved["filepath"])  # não persiste — remove artefato
            raise NotFoundError(f"Prova {prova_id} não encontrada.")
        respostas = {
            "marcadas": result["marked_answers_count"],
            "total_bolhas": result["total_bubbles"],
            "qr": result["qr_data"],
        }
        folha = FolhaRepository.create(
            prova_id=prova_id,
            respostas=respostas,
            imagem_path=saved["filepath"],
        )
        resposta["folha_id"] = folha.id
        resposta["prova_id"] = prova_id
        _audit_v1(
            "PROCESSAR_GABARITO",
            "FolhaResposta",
            folha.id,
            f"prova_id={prova_id} marcadas={result['marked_answers_count']}",
        )
    else:
        # Leitura pura (sem prova_id): remove a cópia em disco após processar
        os.remove(saved["filepath"])

    return jsonify(resposta), 200


@api_v1_bp.route("/resultados", methods=["GET"])
@api_auth
def listar_resultados():
    """Lista resultados/notas processados, com filtro por prova_id e paginação."""
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        raise ValidationError("limit e offset devem ser inteiros.")

    q = FolhaResposta.query
    pid = request.args.get("prova_id", type=int)
    if pid:
        q = q.filter(FolhaResposta.prova_id == pid)

    return jsonify(_paginar(q, limit, offset, "resultados")), 200
