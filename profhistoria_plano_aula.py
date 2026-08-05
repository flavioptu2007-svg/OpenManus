#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProfHistória IA — Gerador de Plano de Aula por Habilidade BNCC (LLM local).

Gera um plano de aula de História completo a partir de uma habilidade BNCC
(ex.: EF07HI12), série e tema, usando o Ollama local (qwen3 / nemotron-mini).

Uso:
    python3 profhistoria_plano_aula.py EF07HI12
    python3 profhistoria_plano_aula.py EF08HI20 --serie 8 --tema "Legado da escravidão"
    python3 profhistoria_plano_aula.py EF06HI10 --model nemotron-mini:latest --html plano.html
"""

import argparse
import json
import os
import sys
import urllib.request


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODELO_PADRAO = os.environ.get("NEMOTRON_MODEL", "qwen3:14b")

PROMPT_SISTEMA = """Você é o ProfHistória IA, um assistente especialista em ensino de História
para os Anos Finais do Ensino Fundamental (6º–9º), EJA e Ensino Médio.
Você domina a BNCC de História e o Currículo Referência de Minas Gerais (CRMG).

Gere SEMPRE um plano de aula em português do Brasil, com estrutura EXATA:

# Plano de Aula — {tema}
**Série:** {serie} | **Habilidade BNCC:** {habilidade}
**Duração:** 50 min

## 1. Objetivos
- (2 a 3 objetivos iniciados por verbo, focados na habilidade)

## 2. Conteúdos
- (tópicos específicos do tema)

## 3. Metodologia / Sequência Didática
- **Abertura (10 min):** (problematização/contextualização)
- **Desenvolvimento (30 min):** (atividade principal)
- **Fechamento (10 min):** (sistematização + conexão com o cotidiano)

## 4. Recursos
- (listar materiais: livro, quadro, fonte histórica, etc.)

## 5. Avaliação
- (critérios observáveis ligados à habilidade)

## 6. Atividade para casa
- (1 atividade que retome a habilidade)

Regras: linguagem adequada à série; conecte sempre que possível com a história
de Minas Gerais/Paracatu; não invente fatos — se não tiver certeza, escreva
"verificar fonte". Use Markdown limpo, sem introdução nem despedida."""


def chamar_ollama(modelo: str, mensagens: list, temperatura: float = 0.4):
    """Chama o Ollama via API nativa /api/chat (stdlib, sem dependências)."""
    payload = {
        "model": modelo,
        "messages": mensagens,
        "stream": False,
        "options": {"temperature": temperatura},
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        dados = json.loads(resp.read().decode("utf-8"))
    return dados["message"]["content"].strip()


def normalizar_habilidade(codigo: str) -> str:
    """Aceita 'EF07HI12' ou 'ef07hi12' -> 'EF07HI12'."""
    return codigo.strip().upper().replace("_", "").replace("-", "")


def gerar_plano(habilidade: str, serie: str, tema: str, modelo: str) -> str:
    if not tema:
        tema = f"Habilidade {habilidade}"
    mensagens = [
        {
            "role": "system",
            "content": PROMPT_SISTEMA.format(
                tema=tema, serie=serie, habilidade=habilidade
            ),
        },
        {
            "role": "user",
            "content": f"Gere o plano de aula da habilidade {habilidade} ({serie} ano), "
            f"tema: {tema}.",
        },
    ]
    print(f"🧠 Gerando plano com {modelo} (isso pode levar 1–2 min em CPU)...")
    return chamar_ollama(modelo, mensagens)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Gerador de Plano de Aula de História por habilidade BNCC (LLM local)."
    )
    p.add_argument("habilidade", help="Código BNCC, ex.: EF07HI12")
    p.add_argument("--serie", default="7", help="Série (6–9, EM, EJA). Padrão: 7")
    p.add_argument("--tema", default="", help="Tema opcional do plano")
    p.add_argument(
        "--model", default=MODELO_PADRAO, help=f"Modelo Ollama. Padrão: {MODELO_PADRAO}"
    )
    p.add_argument("--html", default="", help="Se informado, salva o plano como HTML")
    args = p.parse_args()

    habilidade = normalizar_habilidade(args.habilidade)
    if not habilidade.startswith("EF") or len(habilidade) < 7:
        print(f"⚠️  Habilidade '{habilidade}' parece inválida (esperado ex.: EF07HI12).")

    try:
        plano = gerar_plano(habilidade, args.serie, args.tema, args.model)
    except Exception as e:
        print(f"❌ Erro ao gerar plano: {e}")
        print(
            "   Confirme que o Ollama está rodando:  curl http://localhost:11434/api/tags"
        )
        return 1

    print("\n" + "=" * 72)
    print(plano)
    print("=" * 72)

    if args.html:
        html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>Plano de Aula {habilidade}</title>
<style>body{{font-family:'Segoe UI',sans-serif;max-width:860px;margin:24px auto;padding:0 16px;line-height:1.55;color:#1e2233}}
h1{{color:#4f46e5;border-bottom:3px solid #4f46e5;padding-bottom:8px}}h2{{color:#7c3aed;margin-top:26px}}
li{{margin:4px 0}}code{{background:#eef2ff;padding:1px 6px;border-radius:6px}}</style></head>
<body>
"""
        # Markdown simples -> HTML básico
        for linha in plano.splitlines():
            linha = linha.strip()
            if linha.startswith("# "):
                html += f"<h1>{linha[2:]}</h1>\n"
            elif linha.startswith("## "):
                html += f"<h2>{linha[3:]}</h2>\n"
            elif linha.startswith("- ") or linha.startswith("* "):
                html += f"<li>{linha[2:]}</li>\n"
            elif linha == "---":
                html += "<hr>\n"
            elif linha:
                html += f"<p>{linha}</p>\n"
        html += "</body></html>"
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n📄 Plano salvo em HTML: {args.html}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
