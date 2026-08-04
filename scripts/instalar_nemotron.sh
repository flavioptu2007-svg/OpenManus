#!/usr/bin/env bash
# =====================================================================
# instalar_nemotron.sh — Integração automática do NVIDIA Nemotron
# (HistóriaIA Copilot / OpenManus via Ollama)
#
# Faz, de forma idempotente e não destrutiva:
#   1. Detecta o sistema (OS, RAM, disco, GPU, Python, Node, Docker, Ollama)
#   2. Instala o Ollama caso não exista
#   3. Seleciona o melhor modelo Nemotron conforme a RAM (tabela NVIDIA)
#   4. Executa `ollama pull` do modelo escolhido
#   5. Valida o endpoint OpenAI-compatível do Ollama
#   6. Registra o provider [llm.nemotron] no config.toml (se ausente)
#
# Uso:
#   bash scripts/instalar_nemotron.sh
#   bash scripts/instalar_nemotron.sh --model nemotron-mini:latest
#   bash scripts/instalar_nemotron.sh --check   # só diagnóstico
# =====================================================================
set -euo pipefail

# --- Resolve o diretório do script (relativo/PATH/symlink-safe) ---------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_TOML="$PROJ_ROOT/config/config.toml"

OLLAMA_PORT="${OLLAMA_PORT:-11434}"
MODEL=""
CHECK_ONLY=0

usage() {
  sed -n '2,30p' "$0" | grep -E '^#   ' | sed 's/^#   //'
  echo
  echo "Opções:"
  echo "  --model <nome>   Força um modelo específico (ex.: nemotron:latest)"
  echo "  --check          Apenas diagnostica e sai (não modifica nada)"
  echo "  --help           Mostra esta ajuda"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2 ;;
    --check) CHECK_ONLY=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Opção desconhecida: $1"; usage; exit 1 ;;
  esac
done

# =========================================================================
# 1) DETECÇÃO DO SISTEMA
# =========================================================================
echo "══════════════════════════════════════════════════════════════"
echo " NEMOTRON — INSTALAÇÃO AUTOMÁTICA (HistóriaIA Copilot)"
echo "══════════════════════════════════════════════════════════════"

OS_NAME="$(uname -s)"
OS_DETAIL="$(cat /etc/os-release 2>/dev/null | grep '^PRETTY_NAME=' | cut -d= -f2 | tr -d '"' || echo 'desconhecido')"
RAM_GB="$(awk '/MemTotal/{printf "%.0f", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)"
DISK_GB="$(df -BG "$PROJ_ROOT" 2>/dev/null | awk 'NR==2{gsub(/G/,"",$4); print $4}' || echo 0)"
NPROC="$(nproc 2>/dev/null || echo 0)"

has() { command -v "$1" >/dev/null 2>&1; }

echo "• Sistema      : $OS_NAME ($OS_DETAIL)"
echo "• RAM          : ${RAM_GB} GB"
echo "• Disco livre  : ${DISK_GB} GB"
echo "• CPUs         : $NPROC"

if has nvidia-smi; then
  GPU="$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"
  echo "• GPU NVIDIA   : $GPU"
else
  GPU=""
  echo "• GPU NVIDIA   : não detectada (CPU / iGPU)"
fi

has docker && echo "• Docker       : $(docker --version 2>/dev/null | awk '{print $3}')" || echo "• Docker       : não instalado"
has ollama && echo "• Ollama       : $(ollama --version 2>/dev/null | awk '{print $2}')" || echo "• Ollama       : não instalado"
has python3 && echo "• Python       : $(python3 --version 2>/dev/null | awk '{print $2}')" || echo "• Python       : não instalado"
has node && echo "• Node         : $(node --version 2>/dev/null)" || echo "• Node         : não instalado"
echo "• Open WebUI   : $(curl -s -m 2 -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo 'off')"
echo

if [[ "$CHECK_ONLY" == "1" ]]; then
  echo "[--check] Diagnóstico concluído — nenhuma modificação feita."
  exit 0
fi

# =========================================================================
# 2) INSTALAÇÃO DO OLLAMA (se ausente)
# =========================================================================
if ! has ollama; then
  echo "⚠️  Ollama não encontrado — instalando..."
  case "$OS_NAME" in
    Linux)
      if [[ "$(id -u)" == "0" ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
      else
        echo "→ Instale manualmente: curl -fsSL https://ollama.com/install.sh | sh"
        echo "  (ou use: sudo bash scripts/instalar_nemotron.sh)"
        exit 1
      fi
      ;;
    Darwin)
      echo "→ Baixe o instalador oficial em https://ollama.com/download (macOS)"
      exit 1
      ;;
    *)
      echo "→ Sistema não suportado para instalação automática: $OS_NAME"
      exit 1
      ;;
  esac
  # garante o serviço
  (ollama serve >/dev/null 2>&1 &) || true
  sleep 3
  echo "✅ Ollama instalado."
else
  echo "✅ Ollama já instalado: $(ollama --version 2>/dev/null | awk '{print $2}')"
fi

# Garante que o serviço esteja no ar
if ! curl -s -m 3 "http://localhost:${OLLAMA_PORT}/api/tags" >/dev/null 2>&1; then
  echo "→ Iniciando o serviço Ollama..."
  (ollama serve >/dev/null 2>&1 &) || true
  for _ in $(seq 1 15); do
    curl -s -m 2 "http://localhost:${OLLAMA_PORT}/api/tags" >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -s -m 3 "http://localhost:${OLLAMA_PORT}/api/tags" >/dev/null 2>&1 \
  && echo "✅ Ollama servindo em http://localhost:${OLLAMA_PORT}" \
  || { echo "❌ Não foi possível iniciar o Ollama."; exit 1; }

# =========================================================================
# 3) SELEÇÃO DO MELHOR MODELO NEMOTRON CONFORME O HARDWARE
# =========================================================================
# Tabela NVIDIA (adaptada à RAM):
#   16 GB  -> nemotron-nano   (não publicado no registry do Ollama)
#   32 GB  -> nemotron-mini   (4.2B — recomendado; CPU-friendly)
#   64 GB+ -> nemotron        (70.6B — requer GPU/VRAM elevada)
if [[ -z "$MODEL" ]]; then
  if [[ -n "$GPU" ]]; then
    MODEL="nemotron:latest"      # GPU NVIDIA com VRAM elevada -> Nemotron Super
  elif [[ "$RAM_GB" -ge 64 ]]; then
    MODEL="nemotron:latest"      # 64 GB+ -> Nemotron 70B (com GPU recomendada)
  elif [[ "$RAM_GB" -ge 24 ]]; then
    MODEL="nemotron-mini:latest" # ~30 GB -> Nemotron Mini (CPU-friendly) ✅
  else
    MODEL="nemotron-mini:latest" # fallback seguro para máquinas modestas
  fi
fi
echo "🎯 Modelo selecionado: $MODEL"
echo "   (RAM ${RAM_GB} GB ${GPU:+· GPU NVIDIA: $GPU})"

# =========================================================================
# 4) OLLAMA PULL DO MODELO
# =========================================================================
echo "→ Verificando $MODEL no Ollama..."
if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$MODEL"; then
  echo "✅ $MODEL já está baixado. ($(ollama show "$MODEL" 2>/dev/null | grep -i parameters | head -1))"
else
  echo "→ Baixando $MODEL (pode demorar)..."
  ollama pull "$MODEL"
  echo "✅ Download concluído."
fi

# =========================================================================
# 5) VALIDAÇÃO DO ENDPOINT (OpenAI-compatível)
# =========================================================================
echo "→ Validando endpoint OpenAI-compatível..."
RESP="$(curl -s -m 30 "http://localhost:${OLLAMA_PORT}/v1/models" \
  -H 'Content-Type: application/json' 2>/dev/null || echo '')"
if echo "$RESP" | grep -qi '"id"'; then
  echo "✅ /v1/models OK — Ollama servindo API OpenAI-compatível."
else
  echo "⚠️  /v1/models não respondeu como esperado (verifique o serviço)."
fi

# =========================================================================
# 6) REGISTRO DO PROVIDER NO ROUTER (config.toml)
# =========================================================================
if [[ -f "$CONFIG_TOML" ]] && ! grep -q '\[llm.nemotron\]' "$CONFIG_TOML"; then
  echo "→ Registrando provider [llm.nemotron] em config/config.toml..."
  cat >> "$CONFIG_TOML" <<EOF

# NVIDIA Nemotron (via Ollama) — adicionado por scripts/instalar_nemotron.sh
[llm.nemotron]
api_type = "ollama"
model = "$MODEL"
base_url = "http://localhost:${OLLAMA_PORT}/v1"
api_key = "ollama"
max_tokens = 4096
temperature = 0.0
EOF
  echo "✅ Provider [llm.nemotron] registrado (model=$MODEL)."
elif grep -q '\[llm.nemotron\]' "$CONFIG_TOML"; then
  echo "✅ Provider [llm.nemotron] já registrado no config.toml."
fi

echo
echo "══════════════════════════════════════════════════════════════"
echo " ✅ NEMOTRON PRONTO — modelo: $MODEL"
echo "    Teste rápido:  bash scripts/nemotron_testar.sh"
echo "    Health check:  bash scripts/nemotron_health.sh"
echo "══════════════════════════════════════════════════════════════"
