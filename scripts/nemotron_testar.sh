#!/usr/bin/env bash
# =====================================================================
# nemotron_testar.sh — Testes de capacidades do modelo Nemotron
# (HistóriaIA Copilot)
#
# Aplica 5 perguntas (História, Matemática, Programação, Redação, BNCC),
# mede tempo/tokens e atribui nota 0–10 por rubrica de palavras-chave.
#
# Uso:
#   bash scripts/nemotron_testar.sh                 # modelo do config.toml
#   bash scripts/nemotron_testar.sh nemotron-mini:latest
# =====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(dirname "$SCRIPT_DIR")"

MODEL="${1:-${NEMOTRON_MODEL:-}}"
if [[ -z "$MODEL" ]]; then
  # tenta ler do config.toml ([llm.nemotron] -> [llm])
  MODEL="$(sed -n '/\[llm.nemotron\]/,/^\[/p' "$PROJ_ROOT/config/config.toml" 2>/dev/null | grep '^model' | head -1 | cut -d'=' -f2 | sed 's/#.*//' | tr -d ' \"\"' | xargs)"
fi
MODEL="${MODEL:-nemotron-mini:latest}"
URL="${NEMOTRON_URL:-http://localhost:11434/v1}"
TIMEOUT="${NEMOTRON_TIMEOUT:-300}"

echo "═══ NEMOTRON — TESTES DE CAPACIDADE ═══"
echo "Modelo: $MODEL | Endpoint: $URL"
echo

# --- helper: pergunta ao modelo (OpenAI-compatível, sem streaming) ---
pergunta() {
  # $1 = prompt ; imprime JSON com content + tempos
  local prompt="$1"
  local inicio fim
  inicio=$(date +%s.%N)
  local payload
  payload=$(jq -n --arg m "$MODEL" --arg p "$prompt" \
    '{model:$m, messages:[{role:"user",content:$p}], stream:false, temperature:0.0}' 2>/dev/null \
    || printf '{"model":"%s","messages":[{"role":"user","content":"%s"}],"stream":false,"temperature":0.0}' "$MODEL" "$prompt")
  local resp
  resp=$(curl -s -m "$TIMEOUT" "$URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "$payload" 2>/dev/null || true)
  fim=$(date +%s.%N)
  local segs
  segs=$(echo "$fim - $inicio" | bc 2>/dev/null || echo 0)
  echo "$resp"
  echo "___TEMPO___ ${segs}s"
}

# --- rubrica de avaliação: conta palavras-chave essenciais ---
nota_rubrica() {
  # $1 = resposta ; $2 = lista de palavras-chave (separadas por |)
  # $3 = mínimo de palavras para considerar resposta "substancial" (default 15)
  local resp="$1" keys="$2" min_palavras="${3:-15}"
  local total=0 nkeys n n_palavras
  nkeys=$(echo "$keys" | tr '|' '\n' | grep -c .)
  n_palavras=$(echo "$resp" | wc -w)
  for k in $(echo "$keys" | tr '|' '\n'); do
    if echo "$resp" | grep -qi "$k"; then total=$((total + 1)); fi
  done
  # nota proporcional (mín. 3 por resposta substancial e coerente)
  n=$((total * 10 / nkeys))
  if [[ "$n_palavras" -ge "$min_palavras" ]] && [[ "$n" -lt 3 ]]; then n=3; fi
  if [[ "$n_palavras" -lt 5 ]]; then n=0; fi
  echo "$n"
}

# ============ TESTE 1 — HISTÓRIA ============
echo "──────────────────────────────────────────────"
echo "T1 · HISTÓRIA — 'Explique o que foi o Renascimento e cite duas causas.'"
R1=$(pergunta "Explique em até 4 frases o que foi o Renascimento europeu e cite DUAS causas do seu surgimento. Responda em português.")
N1=$(nota_rubrica "$R1" "renascimento|renascença|renascimento|greco|humanismo|comércio|comercio|imprensa|italia|itália|século|seculo" 20)
echo "Nota T1 (História): $N1/10"
echo "$R1" | head -c 400; echo; echo

# ============ TESTE 2 — MATEMÁTICA ============
echo "──────────────────────────────────────────────"
echo "T2 · MATEMÁTICA — 'Resolva 3x + 12 = 39'"
R2=$(pergunta "Resolva a equação 3x + 12 = 39 e mostre os passos. Responda em português.")
N2=$(nota_rubrica "$R2" "3x|27|x = 9|9|subtrai|passos")
echo "Nota T2 (Matemática): $N2/10"
echo "$R2" | head -c 300; echo; echo

# ============ TESTE 3 — PROGRAMAÇÃO ============
echo "──────────────────────────────────────────────"
echo "T3 · PROGRAMAÇÃO — 'Escreva função Python que inverte uma string'"
R3=$(pergunta "Escreva em Python uma função chamada inverter que recebe uma string e retorna a string invertida. Inclua apenas o código.")
N3=$(nota_rubrica "$R3" "def inverter|return|s[::-1]|reversed|join")
echo "Nota T3 (Programação): $N3/10"
echo "$R3" | head -c 300; echo; echo

# ============ TESTE 4 — REDAÇÃO ============
echo "──────────────────────────────────────────────"
echo "T4 · REDAÇÃO — 'Disserte sobre a importância da leitura'"
R4=$(pergunta "Escreva um parágrafo dissertativo (6 a 8 linhas) sobre a importância da leitura para a formação crítica do cidadão. Responda em português.")
N4=$(nota_rubrica "$R4" "leitura|conhecimento|cidadão|crítico|mundo|formação")
echo "Nota T4 (Redação): $N4/10"
echo "$R4" | head -c 400; echo; echo

# ============ TESTE 5 — BNCC ============
echo "──────────────────────────────────────────────"
echo "T5 · BNCC — 'Habilidade EF06HI12'"
R5=$(pergunta "Descreva a habilidade EF06HI12 da BNCC (História, 6º ano) e sugira uma atividade prática para desenvolvê-la. Responda em português.")
N5=$(nota_rubrica "$R5" "EF06HI12|história|6º|antiguidade|atividade|religião|política")
echo "Nota T5 (BNCC): $N5/10"
echo "$R5" | head -c 400; echo; echo

# ============ MÉDIA FINAL ============
MEDIA=$(echo "scale=1; ($N1 + $N2 + $N3 + $N4 + $N5) / 5" | bc 2>/dev/null || echo 0)
echo "══════════════════════════════════════════════"
echo "  RESULTADO — $MODEL"
echo "  História:      $N1/10"
echo "  Matemática:    $N2/10"
echo "  Programação:   $N3/10"
echo "  Redação:       $N4/10"
echo "  BNCC:          $N5/10"
echo "  ───────────────────────────"
echo "  NOTA GERAL:    $MEDIA/10"
echo "══════════════════════════════════════════════"
