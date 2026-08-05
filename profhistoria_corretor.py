#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProfHistória IA — Corretor Assistido de Questões Discursivas (LLM local).

Corrige respostas dissertativas de História por critérios (rubrica), sugerindo
nota por critério e feedback para o aluno. A IA APOIA — a decisão final é do
professor.

Uso:
    # cria um arquivo JSON (ex.: correcao.json) e roda:
    python3 profhistoria_corretor.py correcao.json
    python3 profhistoria_corretor.py correcao.json --model nemotron-mini:latest
    python3 profhistoria_corretor.py correcao.json --json   # saída JSON

Formato do arquivo JSON:
{
  "questao": "Explique as causas da Revolução Industrial.",
  "resposta_esperada": "Conceitos-chave: capitalismo, cercamentos, máquina a vapor, mão de obra...",
  "criterios": [
    {"nome": "Conteúdo", "max": 6, "descricao": "Domínio dos fatos e conceitos"},
    {"nome": "Argumentação", "max": 3, "descricao": "Causa e consequência, coerência"},
    {"nome": "Uso de fontes/termos", "max": 1, "descricao": "Vocabulário histórico correto"}
  ],
  "respostas": [
    {"aluno": "Maria", "texto": "A Revolução Industrial começou por causa da máquina a vapor..."},
    {"aluno": "João", "texto": "..."}
  ]
}
"""

import argparse
import json
import os
import sys
import urllib.request


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODELO_PADRAO = os.environ.get("NEMOTRON_MODEL", "qwen3:14b")

PROMPT_SISTEMA = """Você é o ProfHistória IA, assistente de correção de questões dissertativas
de História para o Ensino Fundamental (6º–9º) e Médio.

Você recebe: a questão, a resposta esperada (conceitos-chave), uma rubrica com
critérios (nome, nota máxima, descrição) e a resposta de um aluno.

Responda SOMENTE em JSON válido, sem texto fora do JSON:
{
  "notas": {"<nome do criterio>": <nota 0..max>, ...},
  "nota_total": <soma>,
  "feedback_aluno": "<2-3 frases para o aluno, em pt-BR, construtivas>",
  "lacunas": ["<lacuna conceitual 1>", "..."]
}

Regras: seja rigoroso mas justo; não dê a nota máxima se faltar conceito-chave
da resposta esperada; identifique erros conceituais reais (anacronismo, fato
inventado) — se houver invenção, aponte em 'lacunas' e desconte no critério
'Conteúdo'; feedback em linguagem adequada à série; no máximo 3 lacunas."""


def chamar_ollama(modelo: str, mensagens: list) -> dict:
    payload = {
        "model": modelo,
        "messages": mensagens,
        "stream": False,
        "options": {"temperature": 0.2},
        "format": "json",
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        dados = json.loads(resp.read().decode("utf-8"))
    conteudo = dados["message"]["content"].strip()
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError:
        # tenta extrair o bloco JSON entre chaves
        ini, fim = conteudo.find("{"), conteudo.rfind("}")
        if ini != -1 and fim > ini:
            return json.loads(conteudo[ini : fim + 1])
        return {
            "notas": {},
            "feedback_aluno": "Erro ao interpretar a correção.",
            "lacunas": [],
        }


def corrigir(arquivo: str, modelo: str, saida_json: bool) -> int:
    try:
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ Não consegui ler o arquivo: {e}")
        return 1

    questao = dados.get("questao", "")
    esperado = dados.get("resposta_esperada", "")
    criterios = dados.get("criterios", [])
    respostas = dados.get("respostas", [])

    if not respostas or not criterios:
        print("❌ O arquivo precisa de 'criterios' e 'respostas'.")
        return 1

    print(f"🧠 Corrigindo {len(respostas)} resposta(s) com {modelo}...\n")

    resultados = []
    for i, item in enumerate(respostas, 1):
        aluno = item.get("aluno", f"Aluno {i}")
        texto = item.get("texto", "")
        print(f"  [{i}/{len(respostas)}] {aluno}...")
        mensagens = [
            {"role": "system", "content": PROMPT_SISTEMA},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "questao": questao,
                        "resposta_esperada": esperado,
                        "criterios": criterios,
                        "resposta_aluno": texto,
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        try:
            r = chamar_ollama(modelo, mensagens)
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            r = {"notas": {}, "feedback_aluno": f"Erro na correção: {e}", "lacunas": []}
        resultados.append({"aluno": aluno, "texto": texto, "correcao": r})

    if saida_json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return 0

    # Relatório legível
    print("\n" + "=" * 64)
    print("📋 RELATÓRIO DE CORREÇÃO")
    print("=" * 64)
    for item in resultados:
        cor = item["correcao"]
        notas = cor.get("notas", {})
        total = sum(float(v) for v in notas.values())
        maximo = sum(float(c["max"]) for c in criterios)
        print(f"\n👤 {item['aluno']}  —  {total:.1f}/{maximo}")
        for c in criterios:
            v = notas.get(c["nome"], 0)
            barra = "█" * max(0, round(v)) + "░" * max(0, round(c["max"] - v))
            print(f"   {c['nome']:<22} {barra} {v:.1f}/{c['max']}")
        print(f"   💬 Feedback: {cor.get('feedback_aluno', '—')}")
        lacunas = cor.get("lacunas", [])
        lacunas_txt = []
        for l in lacunas[:3]:
            if isinstance(l, dict):
                lacunas_txt.append(l.get("descricao") or l.get("lacuna") or str(l))
            else:
                lacunas_txt.append(str(l))
        if lacunas_txt:
            print(f"   🕳️  Lacunas: {', '.join(lacunas_txt)}")
    print("\n" + "=" * 64)
    print("⚠️  A IA APOIA a correção — revise antes de lançar as notas.")
    print("=" * 64)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Corretor assistido de questões discursivas de História."
    )
    p.add_argument("arquivo", help="Caminho do arquivo JSON com questão + respostas")
    p.add_argument(
        "--model", default=MODELO_PADRAO, help=f"Modelo Ollama. Padrão: {MODELO_PADRAO}"
    )
    p.add_argument(
        "--json", action="store_true", help="Saída em JSON (para integração)"
    )
    args = p.parse_args()
    return corrigir(args.arquivo, args.model, args.json)


if __name__ == "__main__":
    sys.exit(main())
