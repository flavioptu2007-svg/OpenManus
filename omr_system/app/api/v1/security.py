"""Autenticação compatível: X-API-Key (header) OU JWT Bearer.

Uso local/pessoal: a API key é validada contra a variável de ambiente
``GABARITOS_API_KEY``. Endpoints existentes continuam aceitando JWT; a key
é apenas uma alternativa (ou reforço) para ferramentas de automação (MCP).

Nenhuma chave é armazenada em código — apenas lida de variável de ambiente.
"""

import os
from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def _nao_autorizado():
    """Resposta 401 estruturada — criada sob demanda (jsonify exige app context)."""
    return (
        jsonify(
            {
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Não autorizado.",
                    "suggestion": "Envie um JWT Bearer válido ou a API key no header X-API-Key.",
                }
            }
        ),
        401,
    )


def _api_key_valida() -> bool:
    """Valida o header X-API-Key contra GABARITOS_API_KEY (se definida)."""
    expected = os.environ.get("GABARITOS_API_KEY", "").strip()
    if not expected:
        return False
    recebida = request.headers.get("X-API-Key", "")
    return recebida and recebida == expected


def api_auth(fn):
    """Decorator: aceita X-API-Key válida OU JWT válido. Senão, 401 estruturado."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if _api_key_valida():
            return fn(*args, **kwargs)
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            return _nao_autorizado()
        if not get_jwt_identity():
            return _nao_autorizado()
        return fn(*args, **kwargs)

    return wrapper
