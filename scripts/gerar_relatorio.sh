#!/bin/bash
# Gera um relatório de estado do OpenManus (git, ambiente, integrações, testes)
# e o salva com `tee` — exibido no terminal E gravado no arquivo.
#
# Uso:
#   ./scripts/gerar_relatorio.sh                # completo (inclui pytest, ~2min)
#   ./scripts/gerar_relatorio.sh --no-tests     # rápido (pula pytest)
#   ./scripts/gerar_relatorio.sh --out outro.txt
#
# Saída: 0 = ok, 1 = falha.
set -euo pipefail

# ── Convenção do projeto (lib/common.sh) ──────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$PROJECT_ROOT/lib/common.sh" ]; then
    # shellcheck source=lib/common.sh
    source "$PROJECT_ROOT/lib/common.sh"
fi
# PYTHONPATH do sistema (ex.: 3.14) não pode vazar para a venv do projeto
om_unset_pythonpath

OUT_FILE="$PROJECT_ROOT/relatorio.txt"
RUN_TESTS=1

while [ $# -gt 0 ]; do
    case "$1" in
        --no-tests) RUN_TESTS=0 ;;
        --out)
            shift
            OUT_FILE="${1:?--out requer um caminho}"
            ;;
        *) echo "Uso: $0 [--no-tests] [--out arquivo]" >&2; exit 2 ;;
    esac
    shift
done

# ── Normalizar OUT_FILE ───────────────────────────────────────────────────────
# Caminho relativo é resolvido contra a RAIZ do projeto (não contra o CWD do
# chamador), para o arquivo sempre cair dentro do projeto independentemente de
# onde o script for invocado.
case "$OUT_FILE" in
    /*) : ;;                      # absoluto: mantém
    *) OUT_FILE="$PROJECT_ROOT/$OUT_FILE" ;;
esac

# ── Precondições ──────────────────────────────────────────────────────────────
VENV_PY="$PROJECT_ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "❌ Python da venv não encontrado: $VENV_PY" >&2
    echo "   Crie primeiro: uv venv --python 3.12 && uv pip install -r requirements.txt" >&2
    exit 1
fi

# ── Montar e gerar o relatório (tee: tela + arquivo) ──────────────────────────
{
    echo "============================================================"
    echo " RELATORIO DE ESTADO - OpenManus"
    echo " Data: $(date '+%d/%m/%Y %H:%M')"
    echo "============================================================"
    echo
    echo "## 1. GIT"
    echo "--- Branch e historico recente ---"
    git -C "$PROJECT_ROOT" status -sb | head -1
    git -C "$PROJECT_ROOT" log --oneline -5
    echo
    echo "--- Ultimo commit ---"
    git -C "$PROJECT_ROOT" log -1 --format='%h %s%nAutor: %an <%ae>%nData: %ad' --date=short
    echo
    echo "--- Arquivos modificados pendentes ---"
    git -C "$PROJECT_ROOT" status --short | wc -l
    echo "arquivos fora do commit (pre-existentes)"
    echo
    echo "## 2. AMBIENTE PYTHON"
    echo "--- venv ---"
    "$VENV_PY" --version 2>&1
    if [ -f "$PROJECT_ROOT/scripts/instalar_sitecustomize.sh" ]; then
        echo "sitecustomize ativo:"
        "$PROJECT_ROOT/scripts/instalar_sitecustomize.sh" --check 2>&1 | tail -1
    fi
    echo
    echo "--- pip check ---"
    "$VENV_PY" -m pip check 2>&1
    echo "pacotes: $("$VENV_PY" -m pip list 2>/dev/null | tail -n +3 | wc -l)"
    echo
    echo "## 3. INTEGRACOES"
    echo "--- Ollama (servidor systemd) ---"
    curl -s --max-time 5 http://localhost:11434/api/version 2>/dev/null | head -c 60
    echo
    echo "modelos vision:"
    curl -s --max-time 5 http://localhost:11434/api/tags 2>/dev/null | "$VENV_PY" -c "import json,sys; d=json.load(sys.stdin); print(' -', [m['name'] for m in d.get('models',[]) if 'gemma' in m['name'] or 'vision' in m['name'] or 'llava' in m['name']])" 2>/dev/null
    echo
    echo "--- config.toml vision ---"
    if [ -f "$PROJECT_ROOT/config/config.toml" ]; then
        grep -A2 '^\[llm.vision\]' "$PROJECT_ROOT/config/config.toml" | head -3
    fi
    echo
    echo "## 4. TESTES"
    if [ "$RUN_TESTS" = "1" ]; then
        echo "--- resultado pytest ---"
        cd "$PROJECT_ROOT"
        "$VENV_PY" -m pytest tests/ -q --no-header 2>&1 | tail -1
    else
        echo "(pulado — use --no-tests para geração rápida; rode sem a flag para incluir)"
    fi
    echo
    echo "============================================================"
    echo " FIM DO RELATORIO"
    echo "============================================================"
} 2>&1 | tee "$OUT_FILE"

echo "--- (salvo em $OUT_FILE) ---"
