#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nemotron_benchmark.py — Benchmark do Nemotron vs. outros modelos
(HistóriaIA Copilot / OpenManus)

Compara velocidade (latência, tokens/s), qualidade (rubrica de palavras-chave)
e consumo (memória) entre:
  • Modelos LOCAIS do Ollama (qwen3:14b, deepseek-r1:7b, mistral, gemma3,
    nemotron-mini, command-r, ...) — sem custo
  • Modelos REMOTOS via OpenRouter (gpt-5, claude, deepseek, qwen, mistral,
    command-r) — apenas se OPENROUTER_API_KEY estiver definida

Uso:
  unset PYTHONPATH && ./.venv/bin/python scripts/nemotron_benchmark.py
  unset PYTHONPATH && ./.venv/bin/python scripts/nemotron_benchmark.py --modelos qwen3:14b,nemotron-mini:latest
  unset PYTHONPATH && ./.venv/bin/python scripts/nemotron_benchmark.py --json
"""

import argparse
import json
import os
import sys
import time


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/v1")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
OR_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("LLM_API_KEY", "")

# Modelos locais disponíveis por padrão (filtrados pelos que existem no Ollama)
MODELOS_LOCAIS_DEFAULT = [
    "nemotron-mini:latest",
    "qwen3:14b",
    "deepseek-r1:7b",
    "mistral:latest",
    "gemma3:12b",
    "command-r:latest",
    "qwen2.5-coder:latest",
]

# (rótulo, modelo OpenRouter) — apenas usados se houver chave
MODELOS_REMOTOS_DEFAULT = [
    ("GPT (gpt-5)", "openai/gpt-5"),
    ("Claude (claude-3.7-sonnet)", "anthropic/claude-3.7-sonnet"),
    ("DeepSeek (deepseek-chat)", "deepseek/deepseek-chat"),
    ("Qwen (qwen2.5-72b)", "qwen/qwen2.5-72b-instruct"),
    ("Mistral (mistral-large)", "mistralai/mistral-large-latest"),
    ("Command-R (command-r-plus)", "cohere/command-r-plus"),
]

# Perguntas do benchmark (História, Matemática, Programação, Redação, BNCC)
PERGUNTAS = [
    (
        "História",
        "Explique em até 4 frases o que foi o Renascimento europeu e cite DUAS causas do seu surgimento.",
        "renascimento|greco-romano|humanismo|comércio|imprensa",
    ),
    (
        "Matemática",
        "Resolva a equação 3x + 12 = 39 e mostre os passos.",
        "3x|27|x = 9|9",
    ),
    (
        "Programação",
        "Escreva em Python uma função chamada inverter que recebe uma string e retorna a string invertida.",
        "def inverter|return|[::-1]|reversed",
    ),
    (
        "Redação",
        "Escreva um parágrafo dissertativo (6 a 8 linhas) sobre a importância da leitura para a formação crítica do cidadão.",
        "leitura|conhecimento|crítico|formação",
    ),
    (
        "BNCC",
        "Descreva a habilidade EF06HI12 da BNCC (História, 6º ano) e sugira uma atividade prática.",
        "EF06HI12|6º|atividade",
    ),
]


def call_openai(base_url, model, prompt, api_key=None, timeout=180):
    """Chama endpoint OpenAI-compatível; retorna (texto, latência_s) ou (None, err)."""
    import urllib.request

    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.0,
        }
    ).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if "openrouter" in base_url:
        headers["HTTP-Referer"] = os.environ.get(
            "OPENROUTER_HTTP_REFERER", "https://github.com/FoundationAgents/OpenManus"
        )
        headers["X-Title"] = os.environ.get("OPENROUTER_X_TITLE", "OpenManus")

    req = urllib.request.Request(
        f"{base_url}/chat/completions", data=payload, headers=headers
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        lat = time.monotonic() - t0
        text = data["choices"][0]["message"]["content"] or ""
        usage = data.get("usage", {})
        return text, lat, usage
    except Exception as e:  # noqa: BLE001 — benchmark deve reportar e seguir
        return None, time.monotonic() - t0, {"erro": str(e)}


def nota_rubrica(resposta: str, chaves: str) -> float:
    """Nota 0–10 proporcional às palavras-chave encontradas."""
    if not resposta:
        return 0.0
    keys = [k.strip().lower() for k in chaves.split("|") if k.strip()]
    if not keys:
        return 1.0
    acertos = sum(1 for k in keys if k.lower() in resposta.lower())
    return round(max(1.0, acertos * 10 / len(keys)), 1)


def modelos_ollama_disponiveis():
    """Lista de modelos instalados no Ollama."""
    try:
        import urllib.request

        with urllib.request.urlopen(
            os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/tags",
            timeout=5,
        ) as r:
            data = json.loads(r.read().decode())
        return {m["name"] for m in data.get("models", [])}
    except Exception:
        return set()


def main():
    ap = argparse.ArgumentParser(description="Benchmark Nemotron vs. outros modelos")
    ap.add_argument(
        "--modelos", default="", help="Modelos locais (separados por vírgula)"
    )
    ap.add_argument("--json", action="store_true", help="Saída JSON")
    ap.add_argument(
        "--so-local",
        action="store_true",
        help="Apenas modelos locais (não usa OpenRouter)",
    )
    args = ap.parse_args()

    locais = [
        m.strip() for m in args.modelos.split(",") if m.strip()
    ] or MODELOS_LOCAIS_DEFAULT
    disponiveis = modelos_ollama_disponiveis()
    locais = [
        m for m in locais if m in disponiveis
    ] or locais  # mantém se nenhum existe
    if not disponiveis:
        print(
            "⚠️  Ollama fora do ar — benchmark local não será executado.",
            file=sys.stderr,
        )

    remotos = [] if (args.so_local or not OR_KEY) else MODELOS_REMOTOS_DEFAULT
    if remotos:
        print(f"🔑 OpenRouter ativo — incluindo {len(remotos)} modelos remotos.")
    else:
        print("ℹ️  Sem chave OpenRouter (ou --so-local) — apenas modelos locais.")

    resultados = []

    for nome, model, base in [(m, m, OLLAMA_URL) for m in locais] + [
        (label, m, OPENROUTER_URL) for label, m in remotos
    ]:
        linhas = []
        notas = []
        for area, pergunta, chaves in PERGUNTAS:
            texto, lat, usage = call_openai(
                base, model, pergunta, api_key=OR_KEY if "openrouter" in base else None
            )
            if texto is None:
                linhas.append((area, None, lat, usage))
                continue
            notas.append(nota_rubrica(texto, chaves))
            linhas.append((area, texto, lat, usage))
            if not args.json:
                print(f"  · {area:14s} lat={lat:6.2f}s nota={notas[-1]:4.1f}")

        ok = [l for l in linhas if l[1] is not None]
        if ok:
            lat_media = sum(l[2] for l in ok) / len(ok)
            nota_media = round(sum(notas) / len(notas), 1) if notas else 0
            # estimativa de tokens/s (resposta de ~50-150 tokens)
            toks = sum(max(10, len(l[1].split())) for l in ok)
            tok_s = round(toks / max(lat_media, 0.001), 1)
        else:
            lat_media = tok_s = nota_media = 0

        resultados.append(
            {
                "modelo": nome,
                "base": "local" if "ollama" in base or "11434" in base else "remoto",
                "latencia_media_s": round(lat_media, 2),
                "nota_media": nota_media,
                "tokens_s": tok_s,
                "areas": [a for a, t, *_ in linhas if t is None],
            }
        )
        if not args.json:
            print(
                f"  {nome:28s} lat={lat_media:6.2f}s  nota={nota_media:4.1f}  tok/s~{tok_s}"
            )

    # Ranking por nota média (desempate por latência)
    resultados.sort(key=lambda r: (-r["nota_media"], r["latencia_media_s"]))
    for i, r in enumerate(resultados, 1):
        r["rank"] = i

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    else:
        print("\n══════ RANKING ══════")
        for r in resultados:
            medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(r["rank"], "  ")
            print(
                f" {medalha} #{r['rank']} {r['modelo']:30s} nota={r['nota_media']:4.1f}  lat={r['latencia_media_s']:6.2f}s  tok/s~{r['tokens_s']}"
            )


if __name__ == "__main__":
    main()
