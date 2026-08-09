#!/usr/bin/env python3
# coding: utf-8
"""Servidor MCP — Busca na Web com a Brave Search API.

Expõe ferramentas de busca (web, notícias, imagens, vídeos e sugestões)
para qualquer cliente MCP (OpenManus, Claude Desktop, Cursor etc.),
usando o índice de busca independente da Brave — ideal para dar
informação atualizada (grounding) aos agentes de IA.

Configuração:
    export BRAVE_API_KEY="sua-chave"   # obtida em https://brave.com/search/api/

Execução (transporte stdio):
    python3 brave_search_mcp.py

Custo/limites (2026): ~US$ 5/mês de créditos no plano gratuito
(≈ 1.000 buscas), limite padrão de 50 req/s no plano Search.
"""

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("brave-search")

BASE_URL = "https://api.search.brave.com/res/v1"
TIMEOUT_SECONDS = 15
MAX_RESULTS = 20


# ─── Núcleo HTTP ────────────────────────────────────────────────


def _ler_chave_de_arquivo() -> str:
    """Fallback: lê a chave de ~/.brave_api_key (linha crua) ou .env local.

    Necessário porque o cliente stdio do MCP (mcp>=1.0) sanitiza o ambiente
    do subprocesso (apenas PATH/HOME etc.), descartando BRAVE_API_KEY.
    """
    candidatos = [
        os.path.expanduser("~/.brave_api_key"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    ]
    for caminho in candidatos:
        try:
            with open(caminho, encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith("#"):
                        continue
                    if "=" in linha:
                        chave, _, valor = linha.partition("=")
                        if chave.strip() == "BRAVE_API_KEY":
                            v = valor.strip().strip('"').strip("'")
                            if v:
                                return v
                    elif linha.startswith("BSA") and len(linha) > 10:
                        return linha
        except OSError:
            continue
    return ""


def _api_key() -> str:
    """Lê a chave da Brave: env BRAVE_API_KEY, depois arquivos de fallback."""
    chave = os.getenv("BRAVE_API_KEY", "").strip() or _ler_chave_de_arquivo()
    if not chave:
        raise RuntimeError(
            "BRAVE_API_KEY não configurada. Obtenha uma chave gratuita em "
            "https://brave.com/search/api/ e (a) exporte no ambiente "
            "(export BRAVE_API_KEY=BSA-...) ou (b) salve em ~/.brave_api_key."
        )
    return chave


def _mensagem_erro(status: int, corpo: Any) -> str:
    """Transforma status HTTP em mensagem acionável para o modelo."""
    if status == 401:
        return (
            "Erro 401: chave da Brave inválida ou expirada. Verifique sua "
            "BRAVE_API_KEY em https://api-dashboard.search.brave.com/."
        )
    if status in (402, 403):
        return (
            "Erro 402/403: assinatura inativa ou créditos esgotados. Revise o "
            "plano em https://api-dashboard.search.brave.com/."
        )
    if status == 429:
        return (
            "Erro 429: limite de requisições atingido (taxa de 50 req/s ou "
            "cota mensal). Aguarde alguns segundos e tente novamente."
        )
    if 500 <= status < 600:
        return "Erro temporário do servidor da Brave (5xx). Tente novamente."
    # A Brave devolve erros como lista JSON ou como {"error": {...}}
    if isinstance(corpo, list) and corpo and isinstance(corpo[0], dict):
        corpo = corpo[0]
    if isinstance(corpo, dict) and isinstance(corpo.get("error"), dict):
        corpo = corpo["error"]
    if isinstance(corpo, dict):
        msg = corpo.get("message") or corpo.get("error") or corpo.get("detail")
        if isinstance(msg, dict):
            msg = str(msg)
    else:
        msg = None
    if not msg and corpo is not None:
        msg = str(corpo)[:200]
    return f"Erro {status} da Brave: {msg or 'resposta inesperada'}."


async def _buscar(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """Executa uma requisição GET autenticada à API da Brave."""
    headers = {
        "X-Subscription-Token": _api_key(),
        "Accept": "application/json",
        "User-Agent": "brave-search-mcp/1.0",
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.get(
            f"{BASE_URL}/{endpoint}", params=params, headers=headers
        )
        if resp.status_code != 200:
            try:
                corpo = resp.json()
            except Exception:
                corpo = None
            raise RuntimeError(_mensagem_erro(resp.status_code, corpo))
        return resp.json()


def _limpa(texto: str, max_chars: int = 220) -> str:
    """Normaliza e limita um trecho de texto (descrições/snippets)."""
    texto = (texto or "").replace("\r", " ").replace("\n", " ").strip()
    if len(texto) > max_chars:
        return texto[: max_chars - 1].rstrip() + "…"
    return texto


# ─── Formatação de resultados (markdown amigável para LLMs) ─────


def _web_markdown(dados: dict[str, Any]) -> str:
    resultados = (dados.get("web") or {}).get("results") or []
    if not resultados:
        return "Nenhum resultado encontrado."
    linhas = [f"🔎 {len(resultados)} resultado(s) encontrado(s):"]
    for i, r in enumerate(resultados, 1):
        titulo = r.get("title") or "(sem título)"
        url = r.get("url") or ""
        desc = _limpa(r.get("description"))
        snippets = r.get("extra_snippets") or []
        linhas.append(f"\n**{i}. {titulo}**\n{url}\n{desc}")
        for s in snippets[:2]:
            linhas.append(f"   📄 {_limpa(s)}")
        idade = r.get("age") or ""
        if idade:
            linhas.append(f"   🕒 {idade}")
    return "\n".join(linhas)


def _noticias_markdown(dados: dict[str, Any]) -> str:
    resultados = (dados.get("news") or {}).get("results") or []
    if not resultados:
        return "Nenhuma notícia encontrada."
    linhas = [f"📰 {len(resultados)} notícia(s) encontrada(s):"]
    for i, r in enumerate(resultados, 1):
        titulo = r.get("title") or "(sem título)"
        url = r.get("url") or ""
        desc = _limpa(r.get("description"))
        fonte = r.get("source") or {}
        origem = fonte.get("name") if isinstance(fonte, dict) else fonte
        data = r.get("age") or ""
        extras = " · ".join(x for x in (origem, data) if x)
        linhas.append(
            f"\n**{i}. {titulo}**\n{url}\n{desc}" + (f"\n🗞️ {extras}" if extras else "")
        )
    return "\n".join(linhas)


def _imagens_markdown(dados: dict[str, Any]) -> str:
    resultados = (dados.get("images") or {}).get("results") or []
    if not resultados:
        return "Nenhuma imagem encontrada."
    linhas = [f"🖼️ {len(resultados)} imagem(ns) encontrada(s):"]
    for i, r in enumerate(resultados, 1):
        titulo = r.get("title") or "(sem título)"
        url = r.get("url") or ""
        img = r.get("thumbnail") or r.get("image") or {}
        img_url = img.get("src") if isinstance(img, dict) else img
        pagina = r.get("page_age") or ""
        linhas.append(f"\n**{i}. {titulo}**\n{url}")
        if img_url:
            linhas.append(f"🖼️ {img_url}")
        if pagina:
            linhas.append(f"🕒 {pagina}")
    return "\n".join(linhas)


def _videos_markdown(dados: dict[str, Any]) -> str:
    resultados = (dados.get("videos") or {}).get("results") or []
    if not resultados:
        return "Nenhum vídeo encontrado."
    linhas = [f"🎬 {len(resultados)} vídeo(s) encontrado(s):"]
    for i, r in enumerate(resultados, 1):
        titulo = r.get("title") or "(sem título)"
        url = r.get("url") or ""
        desc = _limpa(r.get("description"))
        video = r.get("video") or {}
        duracao = video.get("duration") if isinstance(video, dict) else None
        linhas.append(f"\n**{i}. {titulo}**\n{url}\n{desc}")
        if duracao:
            linhas.append(f"⏱️ {duracao}")
    return "\n".join(linhas)


# ─── Ferramentas MCP ────────────────────────────────────────────


@mcp.tool()
async def brave_web_search(
    query: str,
    count: int = 10,
    country: str = os.getenv("BRAVE_COUNTRY", "br"),
    search_lang: str = os.getenv("BRAVE_LANG", "pt"),
    freshness: str | None = None,
    safesearch: str = "moderate",
    extra_snippets: bool = True,
    offset: int = 0,
) -> str:
    """Busca páginas da web com o índice da Brave.

    Args:
        query: Termos de pesquisa (ex.: "BNCC história 7º ano feudalismo").
        count: Quantidade de resultados (1–20).
        country: Código de país para regionalizar (ex.: "br", "us").
        search_lang: Idioma dos resultados (ex.: "pt", "en").
        freshness: Recência — "pd" (dia), "pw" (semana), "pm" (mês), "py" (ano).
        safesearch: Filtro de conteúdo — "strict", "moderate" ou "off".
        extra_snippets: Inclui trechos extras de contexto (melhor p/ IA).
        offset: Paginação (múltiplo de count).

    Returns:
        Lista formatada em markdown: título, URL, descrição e snippets.
    """
    params: dict[str, Any] = {
        "q": query,
        "count": max(1, min(int(count), MAX_RESULTS)),
        "country": country,
        "search_lang": search_lang,
        "safesearch": safesearch,
        "offset": max(0, int(offset)),
    }
    if freshness:
        params["freshness"] = freshness
    if extra_snippets:
        params["extra_snippets"] = "true"
    dados = await _buscar("web/search", params)
    return _web_markdown(dados)


@mcp.tool()
async def brave_news_search(
    query: str,
    count: int = 10,
    country: str = os.getenv("BRAVE_COUNTRY", "br"),
    search_lang: str = os.getenv("BRAVE_LANG", "pt"),
    freshness: str | None = "pd",
    extra_snippets: bool = True,
) -> str:
    """Busca notícias recentes no índice da Brave.

    Args:
        query: Termos de pesquisa (ex.: "educação Brasil notícias").
        count: Quantidade de resultados (1–20).
        country: Código de país para regionalizar (ex.: "br").
        search_lang: Idioma dos resultados (ex.: "pt").
        freshness: Recência — "pd" (dia), "pw" (semana), "pm" (mês), "py" (ano).
        extra_snippets: Inclui trechos extras de contexto.

    Returns:
        Lista formatada em markdown: título, URL, resumo, veículo e data.
    """
    params: dict[str, Any] = {
        "q": query,
        "count": max(1, min(int(count), MAX_RESULTS)),
        "country": country,
        "search_lang": search_lang,
    }
    if freshness:
        params["freshness"] = freshness
    if extra_snippets:
        params["extra_snippets"] = "true"
    dados = await _buscar("news/search", params)
    return _noticias_markdown(dados)


@mcp.tool()
async def brave_image_search(
    query: str,
    count: int = 10,
    country: str = os.getenv("BRAVE_COUNTRY", "br"),
    search_lang: str = os.getenv("BRAVE_LANG", "pt"),
    safesearch: str = "moderate",
) -> str:
    """Busca imagens com o índice da Brave.

    Args:
        query: Termos de pesquisa (ex.: "charge Brasil império").
        count: Quantidade de resultados (1–20).
        country: Código de país para regionalizar (ex.: "br").
        search_lang: Idioma dos resultados (ex.: "pt").
        safesearch: Filtro de conteúdo — "strict", "moderate" ou "off".

    Returns:
        Lista formatada em markdown: título, URL da página e URL da imagem.
    """
    params: dict[str, Any] = {
        "q": query,
        "count": max(1, min(int(count), MAX_RESULTS)),
        "country": country,
        "search_lang": search_lang,
        "safesearch": safesearch,
    }
    dados = await _buscar("images/search", params)
    return _imagens_markdown(dados)


@mcp.tool()
async def brave_video_search(
    query: str,
    count: int = 10,
    country: str = os.getenv("BRAVE_COUNTRY", "br"),
    search_lang: str = os.getenv("BRAVE_LANG", "pt"),
    freshness: str | None = None,
) -> str:
    """Busca vídeos com o índice da Brave.

    Args:
        query: Termos de pesquisa (ex.: "documentário feudalismo").
        count: Quantidade de resultados (1–20).
        country: Código de país para regionalizar (ex.: "br").
        search_lang: Idioma dos resultados (ex.: "pt").
        freshness: Recência — "pd" (dia), "pw" (semana), "pm" (mês), "py" (ano).

    Returns:
        Lista formatada em markdown: título, URL, descrição e duração.
    """
    params: dict[str, Any] = {
        "q": query,
        "count": max(1, min(int(count), MAX_RESULTS)),
        "country": country,
        "search_lang": search_lang,
    }
    if freshness:
        params["freshness"] = freshness
    dados = await _buscar("videos/search", params)
    return _videos_markdown(dados)


@mcp.tool()
async def brave_autosuggest(
    query: str,
    country: str = os.getenv("BRAVE_COUNTRY", "br"),
    count: int = 10,
) -> str:
    """Sugere termos de pesquisa relacionados (autocompletar).

    Útil para o modelo descobrir como os usuários formulam buscas sobre
    um assunto antes de fazer uma pesquisa completa.

    Args:
        query: Início do termo (ex.: "reforma protes").
        country: Código de país (ex.: "br").
        count: Quantidade de sugestões (1–20).

    Returns:
        Lista de sugestões.
    """
    params: dict[str, Any] = {
        "q": query,
        "count": max(1, min(int(count), MAX_RESULTS)),
        "country": country,
    }
    dados = await _buscar("suggest/search", params)
    sugestoes = dados.get("results") or []
    if not sugestoes:
        return "Nenhuma sugestão encontrada."
    return "💡 Sugestões:\n" + "\n".join(f"- {s}" for s in sugestoes)


# ─── Ponto de entrada ────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
