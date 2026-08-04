"""Servidor MCP ``gabaritos_mcp`` — 7 tools que consomem a API v1.

Transporte: stdio. **Nunca** escrever em stdout (o protocolo MCP usa stdout);
todo diagnóstico vai para stderr via logging.

Rodar::

    python -m mcp_gabaritos

Variáveis de ambiente: GABARITOS_API_URL, GABARITOS_API_KEY.
"""

import logging
import sys
from typing import Any

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from mcp_gabaritos.client import GabaritosClient, GabaritosError
from mcp_gabaritos.formatting import formatar, formatar_erro
from mcp_gabaritos.schemas import (
    CadastrarQuestaoInput,
    ConsultarProvaInput,
    ConsultarQuestoesInput,
    ConsultarResultadosInput,
    CriarProvaInput,
    ListarProvasInput,
    ProcessarGabaritoInput,
)


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gabaritos_mcp")

mcp = FastMCP("gabaritos_mcp")


def _executar(fn: Any, fmt: str, recurso: str):
    """Executa a chamada à API e serializa conforme response_format."""
    try:
        dados = fn()
    except GabaritosError as exc:
        logger.warning("Erro da API: %s", exc)
        return formatar_erro(exc)
    return formatar(dados, fmt, recurso)


# ── tools ────────────────────────────────────────────────────────────────── #


@mcp.tool(
    name="gabaritos_criar_prova",
    annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=False, idempotentHint=False
    ),
    description="Cria uma prova a partir de IDs de questões (ou das não atribuídas). "
    "Use gabaritos_consultar_questoes para listar IDs válidos.",
)
def gabaritos_criar_prova(dados: CriarProvaInput) -> str:
    """Cria uma prova. `question_ids` opcional: se omitido, usa questões não atribuídas."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.criar_prova(dados.nome, dados.question_ids),
            dados.response_format,
            "prova_criada",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_listar_provas",
    annotations=ToolAnnotations(readOnlyHint=True),
    description="Lista provas com paginação (limit/offset).",
)
def gabaritos_listar_provas(dados: ListarProvasInput) -> str:
    """Lista provas paginadas."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.listar_provas(dados.limit, dados.offset),
            dados.response_format,
            "provas",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_consultar_prova",
    annotations=ToolAnnotations(readOnlyHint=True),
    description="Retorna detalhes de uma prova (com questões) pelo ID.",
)
def gabaritos_consultar_prova(dados: ConsultarProvaInput) -> str:
    """Consulta uma prova pelo ID."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.consultar_prova(dados.prova_id),
            dados.response_format,
            "prova",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_consultar_questoes",
    annotations=ToolAnnotations(readOnlyHint=True),
    description="Busca/filtra o banco de questões por matéria, série e dificuldade, "
    "com paginação. Use antes de criar provas ou corrigir gabaritos.",
)
def gabaritos_consultar_questoes(dados: ConsultarQuestoesInput) -> str:
    """Consulta questões com filtros e paginação."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.consultar_questoes(
                dados.materia, dados.serie, dados.dificuldade, dados.limit, dados.offset
            ),
            dados.response_format,
            "questoes",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_cadastrar_questao",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
    description="Cadastra uma nova questão no banco de questões.",
)
def gabaritos_cadastrar_questao(dados: CadastrarQuestaoInput) -> str:
    """Cadastra uma questão nova."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.cadastrar_questao(
                dados.texto,
                dados.habilidade,
                dados.dificuldade,
                dados.materia,
                dados.serie,
            ),
            dados.response_format,
            "questao_criada",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_processar_gabarito",
    annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=False, idempotentHint=False
    ),
    description="Processa a imagem de um gabarito (path local ou base64) e retorna a "
    "leitura estruturada (QR + bolhas). Com prova_id, persiste o resultado "
    "como FolhaResposta (operação que grava).",
)
def gabaritos_processar_gabarito(dados: ProcessarGabaritoInput) -> str:
    """Processa um gabarito a partir de image_path ou image_base64."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.processar_gabarito(
                dados.image_path, dados.image_base64, dados.filename, dados.prova_id
            ),
            dados.response_format,
            "leitura",
        )
    finally:
        cliente.close()


@mcp.tool(
    name="gabaritos_consultar_resultados",
    annotations=ToolAnnotations(readOnlyHint=True),
    description="Lista resultados/notas já processados, com filtro opcional por prova_id.",
)
def gabaritos_consultar_resultados(dados: ConsultarResultadosInput) -> str:
    """Consulta resultados processados (filtro por prova, paginação)."""
    cliente = GabaritosClient()
    try:
        return _executar(
            lambda: cliente.consultar_resultados(
                dados.prova_id, dados.limit, dados.offset
            ),
            dados.response_format,
            "resultados",
        )
    finally:
        cliente.close()


def main() -> None:
    """Entry point: roda o servidor MCP via stdio."""
    logger.info("gabaritos_mcp iniciando via stdio")
    mcp.run()  # transporte stdio (padrão)
