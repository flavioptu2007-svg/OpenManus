#!/bin/bash
# Valida o fluxo completo om + omtest em um único comando (revalidação futura).
# Uso:
#   ./test_om_flow.sh                          # validação padrão
#   ./test_om_flow.sh "sua tarefa aqui"        # prompt customizado
#   ./test_om_flow.sh "tarefa" --verbose       # mostra a saída bruta do omtest
#
# Critérios:
#   1. Aliases om/omtest definidos no ~/.bashrc
#   2. om: cd pro projeto + venv ativo + PYTHONPATH limpo
#   3. omtest: script lança e o agente inicia a execução
#   4. (INFO, não falha) resultado da auth LLM — chave real vs placeholder
#
# O PROMPT padrão pede explicitamente o uso da ferramenta terminate para que
# o agente COMPLETE a tarefa (exit 0) em vez de ficar em loop ou chamar
# ask_human (que bloqueia esperando stdin no harness não-interativo).
# Exit code: 0 se 1-3 passarem; 1 caso contrário. A auth (4) é informativa:
# sem chave real o agente termina com 401 (esperado), mas o fluxo está OK.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
PROMPT="${1:-Responda apenas a palavra OK e imediatamente use a ferramenta terminate para encerrar a tarefa}"
VERBOSE=0
[ "${2:-}" = "--verbose" ] && VERBOSE=1

PROJECT_DIR="$SCRIPT_DIR"
PASS=0
FAIL=0

check() {
    local name="$1" status="$2"
    if [ "$status" = "ok" ]; then
        echo "✅ $name"
        PASS=$((PASS + 1))
    else
        echo "❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "═══════════════════════════════════════════"
echo "🧪 Fluxo om + omtest — revalidação"
echo "═══════════════════════════════════════════"

# ── 1. Aliases (expandem apenas em shell interativo) ───────────────
aliases_out=$(bash -ic 'source ~/.bashrc 2>/dev/null; alias om omtest' 2>/dev/null || true)
if echo "$aliases_out" | grep -q 'alias om=' && echo "$aliases_out" | grep -q 'alias omtest='; then
    check "Aliases om/omtest definidos" ok
else
    check "Aliases om/omtest definidos" fail
    echo "   → obtido: $(echo "$aliases_out" | head -3)"
fi

# ── 2. om: cd pro projeto + venv + PYTHONPATH limpo ────────────────
om_out=$(bash -ic 'source ~/.bashrc 2>/dev/null; om; echo "PWD=$PWD"; which python; echo "PP=${PYTHONPATH:-UNSET}"' 2>/dev/null || true)
# `|| true` em cada pipeline: sem isso, sob `set -euo pipefail`, um grep sem
# match (check falhando) abortaria o script antes dos diagnósticos abaixo.
PWD_LINE=$(echo "$om_out" | grep '^PWD=' | head -1 | cut -d= -f2- || true)
PY_LINE=$(echo "$om_out" | grep -E '^/.*/python$' | head -1 || true)
PP_LINE=$(echo "$om_out" | grep '^PP=' | head -1 | cut -d= -f2- || true)

ok=ok
if [ "$PWD_LINE" != "$PROJECT_DIR" ]; then
    ok=fail
    echo "   → PWD=$PWD_LINE (esperado: $PROJECT_DIR)"
fi
if ! echo "$PY_LINE" | grep -q '\.venv/bin/python'; then
    ok=fail
    echo "   → python não resolveu para o venv: $PY_LINE"
fi
if [ "$PP_LINE" != "UNSET" ]; then
    ok=fail
    echo "   → PYTHONPATH=$PP_LINE (esperado: UNSET)"
fi
check "om: venv ativo + PYTHONPATH limpo" "$ok"
[ "$VERBOSE" = "1" ] && echo "$om_out" | head -6

# ── 3. omtest: script lança e o agente inicia a execução ───────────
tmp=$(mktemp)
set +e
timeout 150 bash -ic "source ~/.bashrc 2>/dev/null; omtest \"$PROMPT\"" >"$tmp" 2>&1
omtest_ret=$?
set -e

intro=$(grep -c 'OpenManus — teste do agente' "$tmp" || true)
step=$(grep -c 'Executing step' "$tmp" || true)

ok=ok
if [ "$intro" -lt 1 ]; then
    ok=fail
    echo "   → intro do omtest não encontrada"
fi
if [ "$step" -lt 1 ]; then
    ok=fail
    echo "   → agente não chegou a 'Executing step 1/20'"
fi
check "omtest: script lança e agente inicia" "$ok"

# ── 4. INFO: resultado da auth LLM ─────────────────────────────────
if grep -q 'Authentication failed. Check API key.' "$tmp"; then
    echo "ℹ️  LLM auth: 401 — chave ausente/placeholder no .env (fluxo OK, agente terminou)"
    echo "   → coloque a chave real:  OPENROUTER_API_KEY=sk-or-v1-...  no .env"
elif [ "$omtest_ret" -eq 0 ]; then
    echo "ℹ️  LLM auth: OK — o agente completou a tarefa (exit 0)"
else
    echo "ℹ️  LLM auth: resposta inesperada (omtest exit=$omtest_ret)"
fi
[ "$VERBOSE" = "1" ] && { echo "── saída do omtest (últimas 15 linhas) ──"; tail -15 "$tmp"; }
rm -f "$tmp"

# ── Resultado ──────────────────────────────────────────────────────
echo "═══════════════════════════════════════════"
if [ "$FAIL" -eq 0 ]; then
    echo "✅ FLUXO OK — $PASS/$PASS checks passaram (auth: ver item 4)"
    exit 0
else
    echo "❌ FLUXO COM FALHAS — $FAIL check(s) falharam, $PASS passaram"
    exit 1
fi
