"""Cliente HTTP da API v1 (httpx) — configuração via variáveis de ambiente.

- ``GABARITOS_API_URL``  (padrão http://127.0.0.1:5000)
- ``GABARITOS_API_KEY``  (header X-API-Key)

Erros da API viram :class:`GabaritosError` com uma ``suggestion`` acionável
para o agente seguir (ex.: "use gabaritos_consultar_questoes para listar IDs").
"""

import os
import pathlib
from typing import Any, Optional

import httpx


DEFAULT_URL = "http://127.0.0.1:5000"


def _env_ou_dotenv(nome: str) -> str:
    """Lê a variável do ambiente; se ausente, procura no `.env` local.

    Alguns clientes MCP (stdio) não repassam o ambiente completo ao
    subprocesso do servidor — este fallback garante que `GABARITOS_API_KEY`
    funcione mesmo quando o servidor for iniciado por um orquestrador.
    """
    valor = os.environ.get(nome, "")
    if valor:
        return valor
    # Busca em ./config/.env, ./.env e omr_system/.env (pai do pacote)
    candidatos = [
        pathlib.Path.cwd() / ".env",
        pathlib.Path.cwd() / "config" / ".env",
        pathlib.Path(__file__).resolve().parent.parent / ".env",
    ]
    for caminho in candidatos:
        try:
            texto = caminho.read_text(encoding="utf-8")
        except OSError:
            continue
        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            if chave.strip() == nome:
                return valor.strip().strip('"').strip("'")
    return ""


class GabaritosError(Exception):
    """Erro da API (HTTP >= 400) ou de conexão, com sugestão acionável."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        status: Optional[int] = None,
    ):
        self.message = message
        self.suggestion = suggestion
        self.status = status
        super().__init__(message)

    def __str__(self) -> str:
        base = self.message
        if self.suggestion:
            base += f" — {self.suggestion}"
        return base


class GabaritosClient:
    """Cliente fino da API v1. Cada método mapeia um endpoint REST."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = (
            base_url or _env_ou_dotenv("GABARITOS_API_URL") or DEFAULT_URL
        ).rstrip("/")
        self.api_key = api_key or _env_ou_dotenv("GABARITOS_API_KEY")
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        self._http = httpx.Client(
            base_url=self.base_url, timeout=timeout, headers=headers
        )

    def close(self) -> None:
        self._http.close()

    # ── núcleo ───────────────────────────────────────────────────────────── #

    def _request(self, method: str, path: str, **kwargs) -> Any:
        try:
            resp = self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise GabaritosError(
                f"Falha de conexão com a API ({self.base_url}): {exc.__class__.__name__}",
                suggestion="Confirme que a API está no ar e que GABARITOS_API_URL está correto.",
            )
        if resp.status_code >= 400:
            self._raise_api_error(resp, path)
        return resp.json()

    def _raise_api_error(self, resp: httpx.Response, path: str = "") -> None:
        try:
            body = resp.json()
        except Exception:
            body = {}
        err = body.get("error") if isinstance(body, dict) else None
        if isinstance(err, dict):  # formato estruturado da API v1
            message = err.get("message", resp.text[:200])
            suggestion = err.get("suggestion")
        else:
            message = str(err) if err else resp.text[:200]
            suggestion = None
        if not suggestion:
            # Sugestão acionável padrão por recurso (endpoints legados sem "suggestion")
            if "/provas" in path:
                suggestion = "Use gabaritos_listar_provas para listar IDs válidos."
            elif "/questoes" in path:
                suggestion = "Use gabaritos_consultar_questoes para listar IDs válidos."
            elif "/resultados" in path:
                suggestion = "Use gabaritos_consultar_resultados para ver os resultados existentes."
            else:
                suggestion = (
                    "Revise os parâmetros e consulte a tool de listagem correspondente."
                )
        raise GabaritosError(
            f"API respondeu {resp.status_code}: {message}",
            suggestion=suggestion,
            status=resp.status_code,
        )

    # ── endpoints ────────────────────────────────────────────────────────── #

    def criar_prova(
        self, nome: Optional[str] = None, question_ids: Optional[list[int]] = None
    ) -> dict:
        payload: dict = {"nome": nome} if nome else {}
        if question_ids:
            payload["question_ids"] = question_ids
        return self._request("POST", "/api/v1/provas", json=payload)

    def listar_provas(self, limit: int = 20, offset: int = 0) -> dict:
        return self._request(
            "GET", "/api/v1/provas", params={"limit": limit, "offset": offset}
        )

    def consultar_prova(self, prova_id: int) -> dict:
        return self._request("GET", f"/api/v1/provas/{prova_id}")

    def consultar_questoes(
        self,
        materia: Optional[str] = None,
        serie: Optional[str] = None,
        dificuldade: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        params = {"limit": limit, "offset": offset}
        if materia:
            params["materia"] = materia
        if serie:
            params["serie"] = serie
        if dificuldade:
            params["dificuldade"] = dificuldade
        return self._request("GET", "/api/v1/questoes", params=params)

    def cadastrar_questao(
        self,
        texto: str,
        habilidade: Optional[str] = None,
        dificuldade: Optional[str] = None,
        materia: Optional[str] = None,
        serie: Optional[str] = None,
    ) -> dict:
        payload = {"texto": texto}
        for chave, valor in (
            ("habilidade", habilidade),
            ("dificuldade", dificuldade),
            ("materia", materia),
            ("serie", serie),
        ):
            if valor is not None:
                payload[chave] = valor
        return self._request("POST", "/api/v1/questoes", json=payload)

    def processar_gabarito(
        self,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,
        filename: Optional[str] = None,
        prova_id: Optional[int] = None,
    ) -> dict:
        import base64

        if not image_path and not image_base64:
            raise GabaritosError(
                "Nenhuma imagem informada.",
                suggestion="Informe image_path (caminho local) ou image_base64.",
            )
        if image_path:
            with open(image_path, "rb") as fh:
                image_base64 = base64.b64encode(fh.read()).decode()
            filename = filename or os.path.basename(image_path)
        payload: dict = {"image_base64": image_base64, "filename": filename}
        if prova_id is not None:
            payload["prova_id"] = prova_id
        return self._request("POST", "/api/v1/gabaritos/processar", json=payload)

    def consultar_resultados(
        self, prova_id: Optional[int] = None, limit: int = 20, offset: int = 0
    ) -> dict:
        params = {"limit": limit, "offset": offset}
        if prova_id is not None:
            params["prova_id"] = prova_id
        return self._request("GET", "/api/v1/resultados", params=params)
