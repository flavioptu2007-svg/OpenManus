"""Formatação das respostas das tools: JSON estruturado ou Markdown legível.

A formatação é por camada (formatting.py) para manter server.py enxuto e
permitir evoluir os dois formatos independentemente.
"""

import json
from typing import Any


# ── utilitários de tabela ────────────────────────────────────────────────── #


def _tabela(colunas: list[tuple[str, str]], linhas: list[dict]) -> str:
    """Monta uma tabela Markdown simples a partir de (header, chave)."""
    if not linhas:
        return "_Nenhum registro encontrado._"
    cab = "| " + " | ".join(c[0] for c in colunas) + " |"
    sep = "|" + "---|" * len(colunas)
    corpo = []
    for linha in linhas:
        cel = []
        for _, chave in colunas:
            val = linha.get(chave)
            cel.append("-" if val is None else str(val))
        corpo.append("| " + " | ".join(cel) + " |")
    return "\n".join([cab, sep, *corpo])


# ── formatadores por recurso ─────────────────────────────────────────────── #


def formatar_prova_criada(data: dict) -> str:
    p = data
    return (
        f"✅ **Prova criada** — ID **{p['id']}**\n\n"
        f"- Nome: {p['nome']}\n"
        f"- Data: {p['data']}\n"
        f"- Questões: {p.get('num_questoes', len(p.get('questoes') or []))}\n"
        f"- Status: {p['status']}"
    )


def formatar_provas(data: dict) -> str:
    provas = data.get("provas", [])
    if not provas:
        return "_Nenhuma prova encontrada._"
    linhas = [
        {
            "ID": p["id"],
            "Nome": p["nome"],
            "Data": p["data"],
            "Questões": p["num_questoes"],
            "Status": p["status"],
        }
        for p in provas
    ]
    corpo = _tabela(
        [
            ("ID", "ID"),
            ("Nome", "Nome"),
            ("Data", "Data"),
            ("Questões", "Questões"),
            ("Status", "Status"),
        ],
        linhas,
    )
    return (
        f"📚 **Provas** ({data.get('total', len(provas))} total)\n\n{corpo}\n\n"
        f"_has_more: {data.get('has_more', False)} · next_offset: {data.get('next_offset')}_"
    )


def formatar_prova(data: dict) -> str:
    questoes = data.get("questoes") or []
    cab = f"📋 **Prova {data['id']} — {data['nome']}**\n\n"
    info = (
        f"- Data: {data['data']}\n"
        f"- Status: {data['status']}\n"
        f"- QRs: {data['qr_code_info'] or '—'}\n"
        f"- Marcações: {data['marked_answers']}"
    )
    if not questoes:
        return cab + info + "\n\n_Sem questões associadas._"
    linhas = [
        {
            "ID": q["id"],
            "Texto": q["texto"][:60],
            "Matéria": q.get("materia") or "—",
            "Série": q.get("serie") or "—",
            "Habilidade": q.get("habilidade") or "—",
        }
        for q in questoes
    ]
    corpo = _tabela(
        [
            ("ID", "ID"),
            ("Texto", "Texto"),
            ("Matéria", "Matéria"),
            ("Série", "Série"),
            ("Habilidade", "Habilidade"),
        ],
        linhas,
    )
    return cab + info + f"\n\n**Questões ({len(questoes)}):**\n\n{corpo}"


def formatar_questoes(data: dict) -> str:
    questoes = data.get("questoes", [])
    if not questoes:
        return "_Nenhuma questão encontrada com esses filtros._"
    linhas = [
        {
            "ID": q["id"],
            "Texto": q["texto"][:70],
            "Matéria": q.get("materia") or "—",
            "Série": q.get("serie") or "—",
            "Dif.": q.get("dificuldade") or "—",
            "Hab.": q.get("habilidade") or "—",
        }
        for q in questoes
    ]
    corpo = _tabela(
        [
            ("ID", "ID"),
            ("Texto", "Texto"),
            ("Matéria", "Matéria"),
            ("Série", "Série"),
            ("Dif.", "Dif."),
            ("Hab.", "Hab."),
        ],
        linhas,
    )
    return (
        f"🗂️ **Questões** ({data.get('total', len(questoes))} total)\n\n{corpo}\n\n"
        f"_has_more: {data.get('has_more', False)} · next_offset: {data.get('next_offset')}_"
    )


def formatar_questao_criada(data: dict) -> str:
    q = data
    return (
        f"✅ **Questão cadastrada** — ID **{q['id']}**\n\n"
        f"- Texto: {q['texto'][:100]}\n"
        f"- Matéria: {q.get('materia') or '—'} · Série: {q.get('serie') or '—'}\n"
        f"- Habilidade: {q.get('habilidade') or '—'} · Dificuldade: {q.get('dificuldade') or '—'}"
    )


def formatar_leitura(data: dict) -> str:
    qrs = ", ".join(data.get("qr_data") or []) or "nenhum"
    return (
        f"🔍 **Leitura do gabarito**\n\n"
        f"- Marcações detectadas: **{data.get('marked_answers_count', 0)}**\n"
        f"- Total de bolhas: {data.get('total_bubbles', 0)}\n"
        f"- Confiança: {data.get('confidence', 0) * 100:.0f}%\n"
        f"- QR codes: {qrs}\n"
        f"- Arquivo: {data.get('image_file', '—')}"
        + (
            f"\n- Registrado como FolhaResposta: **{data.get('folha_id')}** (prova {data.get('prova_id')})"
            if data.get("folha_id")
            else ""
        )
    )


def formatar_resultados(data: dict) -> str:
    folhas = data.get("resultados", [])
    if not folhas:
        return "_Nenhum resultado processado._"
    linhas = [
        {
            "ID": f["id"],
            "Prova": f["prova_id"],
            "Aluno": f.get("aluno_info") or "—",
            "Nota": f.get("nota") if f.get("nota") is not None else "—",
            "Acertos": f.get("acertos", 0),
            "Status": f.get("status", "—"),
        }
        for f in folhas
    ]
    corpo = _tabela(
        [
            ("ID", "ID"),
            ("Prova", "Prova"),
            ("Aluno", "Aluno"),
            ("Nota", "Nota"),
            ("Acertos", "Acertos"),
            ("Status", "Status"),
        ],
        linhas,
    )
    return (
        f"📊 **Resultados** ({data.get('total', len(folhas))} total)\n\n{corpo}\n\n"
        f"_has_more: {data.get('has_more', False)} · next_offset: {data.get('next_offset')}_"
    )


# ── despacho ─────────────────────────────────────────────────────────────── #


def formatar(data: Any, formato: str = "markdown", recurso: str = "") -> str:
    """Serializa a resposta da API no formato pedido.

    ``recurso`` escolhe o formatador markdown (prova_criada, provas, prova,
    questoes, questao_criada, leitura, resultados).
    """
    if formato == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)

    formatadores = {
        "prova_criada": formatar_prova_criada,
        "provas": formatar_provas,
        "prova": formatar_prova,
        "questoes": formatar_questoes,
        "questao_criada": formatar_questao_criada,
        "leitura": formatar_leitura,
        "resultados": formatar_resultados,
    }
    fn = formatadores.get(recurso)
    if fn is None:
        return json.dumps(data, ensure_ascii=False, indent=2)
    try:
        return fn(data)
    except (KeyError, TypeError, AttributeError):
        return json.dumps(data, ensure_ascii=False, indent=2)


def formatar_erro(exc: Exception) -> str:
    """Mensagem de erro acionável (com sugestão) em markdown."""
    msg = str(exc)
    return f"❌ **Erro:** {msg}"
