#!/usr/bin/env bash
# =====================================================================
# nemotron_health.sh — Health Check do Nemotron (HistóriaIA Copilot)
#
# Verifica: porta, latência da API, tempo de resposta, uso de memória,
# tokens/s, e saúde geral do serviço Ollama + modelo Nemotron.
#
# Uso:
#   bash scripts/nemotron_health.sh [modelo]
#   bash scripts/nemotron_health.sh --json   # saída JSON (para dashboard)
# =====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(dirname "$SCRIPT_DIR")"

MODEL="${1:-${NEMOTRON_MODEL:-}}"
[[ -z "$MODEL" ]] && MODEL="$(sed -n '/\[llm.nemotron\]/,/^\[/p' "$PROJ_ROOT/config/config.toml" 2>/dev/null | grep '^model' | head -1 | cut -d'=' -f2 | sed 's/#.*//' | tr -d ' \"\"' | xargs)"
MODEL="${MODEL:-nemotron-mini:latest}"
URL="${NEMOTRON_URL:-http://localhost:11434}"
JSON_OUT=0
[[ "${2:-}" == "--json" || "${1:-}" == "--json" ]] && JSON_OUT=1

status="ok"; porta="off"; latencia_api="n/a"; tempo_resp="n/a"; tok_s="n/a"; ram_mb="n/a"; vram_mb="n/a"; modelo_ativo="nenhum"

# --- 1) PORTA / API ---
if curl -s -m 3 "$URL/api/tags" >/dev/null 2>&1; then
  porta="11434 (ok)"
  latencia_api="$(curl -s -m 3 -o /dev/null -w '%{time_total}' "$URL/api/tags" 2>/dev/null)s"
else
  status="erro: ollama fora do ar"
fi

# --- 2) MODELO ATIVO EM MEMÓRIA (ollama ps) ---
if command -v ollama >/dev/null 2>&1; then
  PS_LINE="$(ollama ps 2>/dev/null | grep -E "$MODEL" | head -1 || true)"
  if [[ -n "$PS_LINE" ]]; then
    modelo_ativo="$(echo "$PS_LINE" | awk '{print $1}')"
    ram_mb="$(echo "$PS_LINE" | awk '{print $3}')"   # coluna SIZE (ex.: 3.3 GB)
    processador="$(echo "$PS_LINE" | awk '{print $4}')"  # 100% CPU / GPU
    if echo "$processador" | grep -qi gpu; then vram_mb="em GPU"; else vram_mb="CPU"; fi
  fi
fi

# --- 3) TEMPO DE RESPOSTA + TOKENS/S (API nativa do Ollama: /api/chat) ---
if [[ "$porta" != "off" ]]; then
  payload=$(printf '{"model":"%s","messages":[{"role":"user","content":"Diga apenas: pong"}],"stream":false,"options":{"temperature":0.0}}' "$MODEL")
  resp=$(curl -s -m 300 "$URL/api/chat" -H 'Content-Type: application/json' -d "$payload" 2>/dev/null || true)
  if echo "$resp" | grep -q '"message"'; then
    total_ns=$(echo "$resp" | grep -o '"total_duration":[0-9]*' | head -1 | cut -d: -f2 || true)
    eval_n=$(echo "$resp" | grep -o '"eval_count":[0-9]*' | head -1 | cut -d: -f2 || true)
    eval_ns=$(echo "$resp" | grep -o '"eval_duration":[0-9]*' | head -1 | cut -d: -f2 || true)
    if [[ -n "$total_ns" && "$total_ns" != "0" ]]; then
      tempo_resp="$(echo "scale=2; $total_ns / 1000000000" | bc 2>/dev/null || echo "n/a")s"
    fi
    if [[ -n "$eval_n" && -n "$eval_ns" && "$eval_ns" != "0" ]]; then
      tok_s=$(echo "scale=1; $eval_n * 1000000000 / $eval_ns" | bc 2>/dev/null || echo "n/a")
    fi
  else
    status="erro: modelo não respondeu (primeira carga pode demorar)"
  fi
fi

# --- 4) MEMÓRIA DO SISTEMA ---
mem_total="$(awk '/MemTotal/{printf "%.0f", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)"
mem_livre="$(awk '/MemAvailable/{printf "%.0f", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)"

if [[ "$JSON_OUT" == "1" ]]; then
  cat <<EOF
{"model":"$MODEL","status":"$status","porta":"$porta","latencia_api":"$latencia_api","tempo_resposta":"$tempo_resp","tokens_s":"$tok_s","ram_modelo":"$ram_mb","vram":"$vram_mb","modelo_ativo":"$modelo_ativo","ram_total_gb":"$mem_total","ram_livre_gb":"$mem_livre"}
EOF
  exit 0
fi

echo "══════ NEMOTRON — HEALTH CHECK ══════"
echo "Modelo alvo   : $MODEL"
echo "Status        : $status"
echo "Porta         : $porta"
echo "Latência API  : $latencia_api"
echo "Tempo resposta: $tempo_resp"
echo "Tokens/s      : $tok_s"
echo "RAM do modelo : $ram_mb"
echo "VRAM          : $vram_mb"
echo "Modelo ativo  : $modelo_ativo"
echo "RAM sistema   : ${mem_livre}GB livres de ${mem_total}GB"
echo "════════════════════════════════════════"
[[ "$status" == "ok" ]] && exit 0 || exit 1
